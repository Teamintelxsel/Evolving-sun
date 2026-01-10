from pathlib import Path
import json
from src.orchestrator import BenchmarkOrchestrator


def main():
    orch = BenchmarkOrchestrator(tasks_file="tasks.yaml", output_dir="logs/benchmarks")
    consolidated = orch.execute_all_suites()
    orch.print_summary(consolidated)
    orch.save_results(consolidated)

    # Write per-suite JSONs and print scores
    for suite_key, suite in consolidated.get("suites", {}).items():
        suite_out = {
            "watermark": consolidated["watermark"],
            "provenance": consolidated["provenance"],
            "suite": suite,
        }
        out_file = Path("logs/benchmarks") / f"{suite_key}_results.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(suite_out, f, indent=2)

        # Print percentage score if well-defined
        if suite_key == "swebench":
            total = suite.get("total_tasks", 0)
            passed = sum(
                shard.get("results", {}).get("passed", 0)
                for shard in suite.get("shard_results", [])
            )
            score = round(100.0 * passed / total, 2) if total else 0.0
            print(f"swebench_verified: {score}%")
        elif suite_key == "gpqa":
            acc = suite.get("results", {}).get("accuracy", 0.0)
            score = round(acc * 100.0, 2)
            print(f"gpqa_diamond: {score}%")
        elif suite_key == "kegg":
            print("kegg_ko01100: metrics recorded (no % score)")


if __name__ == "__main__":
    main()
