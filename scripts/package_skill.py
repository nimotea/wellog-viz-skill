#!/usr/bin/env python3
"""
Skill Packager - Creates a distributable .skill file of a skill folder

Usage:
    python utils/package_skill.py <path/to/skill-folder> [output-directory]

Example:
    python utils/package_skill.py skills/public/my-skill
    python utils/package_skill.py skills/public/my-skill ./dist
"""

import sys
import zipfile
import shutil
import json
from pathlib import Path
from quick_validate import validate_skill


def package_skill(skill_path, output_dir=None):
    """
    Package a skill folder into a .skill file AND a build directory for npm link.
    """
    skill_path = Path(skill_path).resolve()

    # Validate skill folder exists
    if not skill_path.exists():
        print(f"❌ Error: Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"❌ Error: Path is not a directory: {skill_path}")
        return None

    # Validate SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ Error: SKILL.md not found in {skill_path}")
        return None

    # Run validation before packaging
    print("🔍 Validating skill...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"❌ Validation failed: {message}")
        print("   Please fix the validation errors before packaging.")
        return None
    print(f"✅ {message}\n")

    # Determine output location
    skill_name = skill_path.name
    
    # 0. Get version from root package.json
    version = "1.0.0"
    root_package_json = skill_path / "package.json"
    if root_package_json.exists():
        try:
            with open(root_package_json, "r", encoding="utf-8") as f:
                root_info = json.load(f)
                version = root_info.get("version", "1.0.0")
            print(f"🔖 Detected version: {version}")
        except Exception as e:
            print(f"⚠️ Warning: Could not read version from package.json: {e}")

    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    # 1. Prepare build directory for npm link
    build_dir = skill_path / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🏗️  Preparing build directory: {build_dir}")

    skill_filename = output_path / f"{skill_name}-{version}.skill"

    # Create the .skill file (zip format) and copy to build dir
    try:
        with zipfile.ZipFile(skill_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the skill directory
            for file_path in skill_path.rglob('*'):
                # Check if file should be ignored
                if "rules" in file_path.parts or ".git" in file_path.parts or "__pycache__" in file_path.parts:
                    continue
                
                if ".trae" in file_path.parts or file_path.name == "feedback_logs.jsonl":
                    continue

                if "skill-creator" in file_path.parts:
                    continue
                
                # Exclude build directory itself to avoid recursion
                if "build" in file_path.parts:
                    continue

                # Exclude build scripts
                if file_path.name in ["package_skill.py", "init_skill.py", "quick_validate.py"]:
                    continue

                # Exclude git configuration files
                if file_path.name in [".gitignore", ".gitmodules"]:
                    continue

                # Exclude the entire upstream-src directory
                if "upstream-src" in file_path.parts:
                    continue

                # Exclude any existing .skill files
                if file_path.suffix == '.skill':
                    continue

                if file_path.is_file():
                    # Relative path for zip
                    arcname = file_path.relative_to(skill_path.parent)
                    zipf.write(file_path, arcname)
                    
                    # Relative path for build dir
                    rel_path = file_path.relative_to(skill_path)
                    dest_path = build_dir / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_path)
                    
                    print(f"  Added: {rel_path}")

        # 2. Create package.json in build directory for npm link
        package_info = {
            "name": f"wellog-viz-skill",
            "version": version,
            "description": "Wellog Visualisation Skill Documentation and Patterns",
            "private": True
        }
        with open(build_dir / "package.json", "w", encoding="utf-8") as f:
            json.dump(package_info, f, indent=2)
        print(f"📄 Created package.json in build directory")

        print(f"\n✅ Successfully packaged skill to: {skill_filename}")
        print(f"✅ Build directory ready at: {build_dir}")
        print(f"👉 You can now run 'npm link' inside the build directory.")
        return skill_filename

    except Exception as e:
        print(f"❌ Error creating .skill file or build directory: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python utils/package_skill.py <path/to/skill-folder> [output-directory]")
        print("\nExample:")
        print("  python utils/package_skill.py skills/public/my-skill")
        print("  python utils/package_skill.py skills/public/my-skill ./dist")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"📦 Packaging skill: {skill_path}")
    if output_dir:
        print(f"   Output directory: {output_dir}")
    print()

    result = package_skill(skill_path, output_dir)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
