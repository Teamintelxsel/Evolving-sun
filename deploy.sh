#!/bin/bash
# Deployment Script for Evolving-sun Platform
# Version: 1.0
# Last Updated: January 4, 2026

set -e  # Exit on any error
set -u  # Exit on undefined variables
set -o pipefail  # Exit on pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_VERSION="3.10"
REQUIRED_PYTHON="python3"
VENV_DIR="venv"
AUDIT_SCORE_THRESHOLD="85.0"

# Functions
echo_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

echo_success() {
    echo -e "${GREEN}✓${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo_error() {
    echo -e "${RED}✗${NC} $1"
}

echo_section() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    echo_section "Checking Prerequisites"
    
    # Check Python version
    if ! command -v $REQUIRED_PYTHON &> /dev/null; then
        echo_error "Python 3 is not installed"
        exit 1
    fi
    
    PYTHON_VER=$($REQUIRED_PYTHON --version 2>&1 | awk '{print $2}')
    echo_info "Python version: $PYTHON_VER"
    
    # Check Git
    if ! command -v git &> /dev/null; then
        echo_error "Git is not installed"
        exit 1
    fi
    
    GIT_VER=$(git --version | awk '{print $3}')
    echo_info "Git version: $GIT_VER"
    
    echo_success "Prerequisites check passed"
}

# Setup virtual environment
setup_virtualenv() {
    echo_section "Setting Up Virtual Environment"
    
    if [ -d "$VENV_DIR" ]; then
        echo_warning "Virtual environment already exists, using existing"
    else
        echo_info "Creating virtual environment..."
        $REQUIRED_PYTHON -m venv $VENV_DIR
        echo_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source $VENV_DIR/bin/activate
    echo_success "Virtual environment activated"
    
    # Upgrade pip
    echo_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    echo_success "Pip upgraded"
}

# Install dependencies
install_dependencies() {
    echo_section "Installing Dependencies"
    
    if [ ! -f "requirements.txt" ]; then
        echo_error "requirements.txt not found"
        exit 1
    fi
    
    echo_info "Installing Python packages..."
    pip install -r requirements.txt
    echo_success "Dependencies installed"
}

# Run tests
run_tests() {
    echo_section "Running Test Suite"
    
    if [ -f "test_comprehensive_audit.py" ]; then
        echo_info "Running comprehensive audit tests..."
        python3 -m pytest test_comprehensive_audit.py -v
        echo_success "All tests passed"
    else
        echo_warning "Test file not found, skipping tests"
    fi
}

# Run security checks
run_security_checks() {
    echo_section "Running Security Checks"
    
    echo_info "Running pip-audit for dependency vulnerabilities..."
    if command -v pip-audit &> /dev/null; then
        pip-audit || echo_warning "Vulnerabilities found, review recommended"
    else
        echo_warning "pip-audit not installed, skipping"
    fi
    
    echo_info "Running bandit for security issues..."
    if command -v bandit &> /dev/null; then
        bandit -r . -ll || echo_warning "Security issues found, review recommended"
    else
        echo_warning "bandit not installed, skipping"
    fi
    
    echo_success "Security checks complete"
}

# Run comprehensive audit
run_audit() {
    echo_section "Running Comprehensive Audit"
    
    if [ -f "comprehensive_audit.py" ]; then
        echo_info "Running comprehensive audit..."
        python3 comprehensive_audit.py
        
        # Check if audit report was generated
        if [ -d "audit_reports" ]; then
            echo_success "Audit completed, reports generated in audit_reports/"
            
            # Extract quality score if available
            # This is a placeholder - actual implementation depends on audit output format
            echo_info "Review audit reports for quality score and recommendations"
        else
            echo_warning "Audit completed but no reports directory found"
        fi
    else
        echo_warning "comprehensive_audit.py not found, skipping audit"
    fi
}

# Run code quality checks
run_quality_checks() {
    echo_section "Running Code Quality Checks"
    
    # Flake8
    echo_info "Running flake8..."
    if command -v flake8 &> /dev/null; then
        flake8 . --exclude=$VENV_DIR,build,dist --max-line-length=100 || echo_warning "Linting issues found"
    else
        echo_warning "flake8 not installed, skipping"
    fi
    
    # Black (check only, no formatting)
    echo_info "Checking code formatting with black..."
    if command -v black &> /dev/null; then
        black --check . --exclude=$VENV_DIR || echo_warning "Formatting issues found"
    else
        echo_warning "black not installed, skipping"
    fi
    
    echo_success "Quality checks complete"
}

# Generate reports
generate_reports() {
    echo_section "Generating Reports"
    
    if [ -f "comprehensive_audit.py" ]; then
        echo_info "Generating audit reports..."
        python3 comprehensive_audit.py --generate-reports
        echo_success "Reports generated"
    else
        echo_warning "comprehensive_audit.py not found, skipping report generation"
    fi
}

# Git operations
git_operations() {
    echo_section "Git Operations"
    
    # Check git status
    echo_info "Checking git status..."
    git status --short
    
    # Check if on main branch
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo_info "Current branch: $CURRENT_BRANCH"
    
    if [ "$CURRENT_BRANCH" != "main" ]; then
        echo_warning "Not on main branch, deployment should typically be from main"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo_error "Deployment cancelled"
            exit 1
        fi
    fi
    
    # Check for uncommitted changes
    if [[ -n $(git status -s) ]]; then
        echo_warning "Uncommitted changes detected"
        git status --short
        read -p "Continue with uncommitted changes? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo_error "Deployment cancelled - commit changes first"
            exit 1
        fi
    fi
    
    echo_success "Git checks passed"
}

# Create release tag
create_release_tag() {
    echo_section "Creating Release Tag"
    
    # Get version from user or environment
    if [ -z "${VERSION:-}" ]; then
        echo_info "Current tags:"
        git tag -l | tail -5
        echo ""
        read -p "Enter version tag (e.g., v1.0.0): " VERSION
    fi
    
    if [ -z "$VERSION" ]; then
        echo_warning "No version provided, skipping tag creation"
        return
    fi
    
    # Check if tag already exists
    if git rev-parse "$VERSION" >/dev/null 2>&1; then
        echo_error "Tag $VERSION already exists"
        exit 1
    fi
    
    # Create annotated tag
    echo_info "Creating tag $VERSION..."
    git tag -a "$VERSION" -m "Production Release $VERSION"
    
    # Push tag
    read -p "Push tag to origin? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin "$VERSION"
        echo_success "Tag $VERSION created and pushed"
    else
        echo_info "Tag $VERSION created locally (not pushed)"
    fi
}

# Deployment summary
deployment_summary() {
    echo_section "Deployment Summary"
    
    echo_info "Deployment Environment:"
    echo "  - Python: $($REQUIRED_PYTHON --version)"
    echo "  - Git Branch: $(git rev-parse --abbrev-ref HEAD)"
    echo "  - Git Commit: $(git rev-parse --short HEAD)"
    echo "  - Working Directory: $(pwd)"
    echo "  - Virtual Environment: $VENV_DIR"
    
    if [ -d "audit_reports" ]; then
        echo ""
        echo_info "Latest Audit Reports:"
        ls -lh audit_reports/ | tail -5
    fi
    
    echo ""
    echo_success "Deployment process complete!"
    echo ""
    echo_info "Next steps:"
    echo "  1. Review audit reports in audit_reports/"
    echo "  2. Verify all tests passed"
    echo "  3. Check for security vulnerabilities"
    echo "  4. Monitor logs after deployment"
    echo "  5. Update documentation if needed"
}

# Main deployment flow
main() {
    echo ""
    echo_section "🚀 Evolving-sun Deployment Script"
    echo_info "Starting deployment process..."
    echo ""
    
    # Run deployment steps
    check_prerequisites
    git_operations
    setup_virtualenv
    install_dependencies
    run_quality_checks
    run_security_checks
    run_tests
    run_audit
    generate_reports
    
    # Optional: Create release tag
    read -p "Create release tag? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_release_tag
    fi
    
    deployment_summary
    
    echo ""
    echo_success "✅ Deployment complete!"
    echo ""
}

# Run main function
main "$@"
