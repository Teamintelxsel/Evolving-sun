"""Automated Key Rotation - Lifecycle management for PQC keys."""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from security.pqc.dilithium_signer import DilithiumSigner
from security.pqc.kyber_vault import KyberVault

logger = logging.getLogger(__name__)


class KeyRotationManager:
    """Manages automated rotation of PQC keys."""

    def __init__(
        self,
        vault: Optional[KyberVault] = None,
        signer: Optional[DilithiumSigner] = None,
        rotation_config_path: str = "config/key_rotation.json",
    ) -> None:
        """Initialize key rotation manager.

        Args:
            vault: KyberVault instance
            signer: DilithiumSigner instance
            rotation_config_path: Path to rotation configuration
        """
        self.vault = vault or KyberVault()
        self.signer = signer or DilithiumSigner()
        self.rotation_config_path = Path(rotation_config_path)
        self.rotation_history: List[Dict[str, Any]] = []
        self._load_config()

    def _load_config(self) -> None:
        """Load rotation configuration."""
        if self.rotation_config_path.exists():
            with open(self.rotation_config_path) as f:
                self.config = json.load(f)
        else:
            # Default configuration
            self.config = {
                "encryption_keys": {
                    "rotation_interval_days": 180,  # 6 months
                    "warning_days": 30,
                },
                "signing_keys": {
                    "rotation_interval_days": 365,  # 1 year
                    "warning_days": 60,
                },
                "emergency_rotation_enabled": True,
                "auto_backup": True,
            }
            self._save_config()

    def _save_config(self) -> None:
        """Save rotation configuration."""
        self.rotation_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.rotation_config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def check_rotation_needed(self, key_id: str, key_type: str) -> Dict[str, Any]:
        """Check if a key needs rotation.

        Args:
            key_id: Key identifier
            key_type: 'encryption' or 'signing'

        Returns:
            Dictionary with rotation status
        """
        # In production, retrieve key metadata from Vault
        # For now, simulate based on configuration

        config_key = f"{key_type}_keys"
        rotation_interval = self.config[config_key]["rotation_interval_days"]
        warning_days = self.config[config_key]["warning_days"]

        # Simulate key age (in production, get from metadata)
        key_age_days = 150  # Placeholder

        needs_rotation = key_age_days >= rotation_interval
        warning = key_age_days >= (rotation_interval - warning_days)

        return {
            "key_id": key_id,
            "key_type": key_type,
            "age_days": key_age_days,
            "rotation_interval_days": rotation_interval,
            "needs_rotation": needs_rotation,
            "warning": warning,
            "days_until_rotation": rotation_interval - key_age_days,
        }

    def rotate_encryption_key(self, old_key_id: str) -> Dict[str, Any]:
        """Rotate an encryption key.

        Args:
            old_key_id: Current key identifier

        Returns:
            Rotation result
        """
        logger.info(f"Rotating encryption key: {old_key_id}")

        # Generate new keypair
        new_keypair = self.vault.generate_keypair()
        new_key_id = f"{old_key_id}_rotated_{datetime.utcnow().strftime('%Y%m%d')}"

        # Store new keypair in vault
        self.vault.store_keypair_in_vault(new_keypair, new_key_id)

        # Backup old key if enabled
        if self.config.get("auto_backup"):
            self._backup_key(old_key_id, "encryption")

        # Record rotation
        rotation_record = {
            "old_key_id": old_key_id,
            "new_key_id": new_key_id,
            "key_type": "encryption",
            "timestamp": datetime.utcnow().isoformat(),
            "reason": "scheduled_rotation",
        }
        self.rotation_history.append(rotation_record)

        logger.info(f"Encryption key rotated: {old_key_id} -> {new_key_id}")

        return {
            "success": True,
            "old_key_id": old_key_id,
            "new_key_id": new_key_id,
            "timestamp": rotation_record["timestamp"],
        }

    def rotate_signing_key(self, old_key_id: str) -> Dict[str, Any]:
        """Rotate a signing key.

        Args:
            old_key_id: Current key identifier

        Returns:
            Rotation result
        """
        logger.info(f"Rotating signing key: {old_key_id}")

        # Generate new keypair
        new_keypair = self.signer.generate_keypair()
        new_key_id = f"{old_key_id}_rotated_{datetime.utcnow().strftime('%Y%m%d')}"

        # In production, store in Vault
        # For now, save to disk (demonstration)
        keys_dir = Path("keys")
        keys_dir.mkdir(exist_ok=True)

        with open(keys_dir / f"{new_key_id}.pub", "wb") as f:
            f.write(new_keypair["public_key"])

        # Backup old key
        if self.config.get("auto_backup"):
            self._backup_key(old_key_id, "signing")

        # Record rotation
        rotation_record = {
            "old_key_id": old_key_id,
            "new_key_id": new_key_id,
            "key_type": "signing",
            "timestamp": datetime.utcnow().isoformat(),
            "reason": "scheduled_rotation",
        }
        self.rotation_history.append(rotation_record)

        logger.info(f"Signing key rotated: {old_key_id} -> {new_key_id}")

        return {
            "success": True,
            "old_key_id": old_key_id,
            "new_key_id": new_key_id,
            "timestamp": rotation_record["timestamp"],
            "public_key_path": str(keys_dir / f"{new_key_id}.pub"),
        }

    def emergency_rotation(self, key_id: str, key_type: str, reason: str) -> Dict[str, Any]:
        """Perform emergency key rotation.

        Args:
            key_id: Key to rotate
            key_type: 'encryption' or 'signing'
            reason: Reason for emergency rotation

        Returns:
            Rotation result
        """
        if not self.config.get("emergency_rotation_enabled"):
            logger.error("Emergency rotation is disabled")
            return {"success": False, "error": "Emergency rotation disabled"}

        logger.warning(f"EMERGENCY ROTATION: {key_id} ({reason})")

        # Perform rotation based on type
        if key_type == "encryption":
            result = self.rotate_encryption_key(key_id)
        elif key_type == "signing":
            result = self.rotate_signing_key(key_id)
        else:
            return {"success": False, "error": f"Unknown key type: {key_type}"}

        # Update rotation record with emergency flag
        if self.rotation_history:
            self.rotation_history[-1]["reason"] = f"EMERGENCY: {reason}"
            self.rotation_history[-1]["emergency"] = True

        # Send alerts (placeholder)
        self._send_rotation_alert(key_id, reason, emergency=True)

        return result

    def _backup_key(self, key_id: str, key_type: str) -> None:
        """Backup a key before rotation.

        Args:
            key_id: Key identifier
            key_type: Key type
        """
        backup_dir = Path("backups/keys")
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{key_id}_{timestamp}.backup"

        # In production, retrieve from Vault and encrypt backup
        logger.info(f"Backing up key to: {backup_path}")

        with open(backup_path, "w") as f:
            json.dump(
                {
                    "key_id": key_id,
                    "key_type": key_type,
                    "timestamp": timestamp,
                    "note": "Encrypted backup (production would contain actual key material)",
                },
                f,
                indent=2,
            )

    def _send_rotation_alert(
        self, key_id: str, reason: str, emergency: bool = False
    ) -> None:
        """Send alert about key rotation.

        Args:
            key_id: Key identifier
            reason: Rotation reason
            emergency: Whether this is an emergency rotation
        """
        # In production, integrate with alerting system
        severity = "CRITICAL" if emergency else "INFO"
        logger.info(f"[{severity}] Key rotation alert: {key_id} - {reason}")

    def get_rotation_schedule(self) -> List[Dict[str, Any]]:
        """Get upcoming rotation schedule.

        Returns:
            List of upcoming rotations
        """
        # In production, query Vault for all keys and their ages
        schedule = [
            {
                "key_id": "production-master-key",
                "key_type": "encryption",
                "next_rotation": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "priority": "high",
            },
            {
                "key_id": "commit-signing-key",
                "key_type": "signing",
                "next_rotation": (datetime.utcnow() + timedelta(days=90)).isoformat(),
                "priority": "medium",
            },
        ]
        return schedule

    def get_rotation_history(self) -> List[Dict[str, Any]]:
        """Get rotation history.

        Returns:
            List of past rotations
        """
        return self.rotation_history

    def run_rotation_check(self) -> Dict[str, Any]:
        """Run automated rotation check for all keys.

        Returns:
            Summary of rotation actions
        """
        logger.info("Running automated rotation check")

        rotations_needed = []
        warnings = []

        # Check all keys (placeholder - in production, query Vault)
        test_keys = [
            ("production-master-key", "encryption"),
            ("commit-signing-key", "signing"),
        ]

        for key_id, key_type in test_keys:
            status = self.check_rotation_needed(key_id, key_type)

            if status["needs_rotation"]:
                rotations_needed.append(status)
            elif status["warning"]:
                warnings.append(status)

        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "rotations_needed": len(rotations_needed),
            "warnings": len(warnings),
            "details": {"rotations": rotations_needed, "warnings": warnings},
        }

        logger.info(
            f"Rotation check complete: {len(rotations_needed)} rotations needed, "
            f"{len(warnings)} warnings"
        )

        return summary
