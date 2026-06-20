#!/usr/bin/env python3
"""
CLI Chunker - Project to BEJSON 104db Packager & Rebuilder
OVERHAULED: Versioned Project Storage System with Numeric Indexing
"""
import os
import sys
import json
import argparse
import time
import random
import shutil
from pathlib import Path

# Setup local library path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / "lib"))

try:
    import lib_bejson_core as BEJSONCore
    import lib_bejson_utility as Utility
    import lib_bejson_validator as Validator
except ImportError:
    print("CRITICAL: Local libraries not found in lib/")
    sys.exit(1)

PROJECTS_DIR = BASE_DIR / "Projects"
HISTORY_FILE = BASE_DIR / "chunk_history.104a.bejson"
REGISTRY_FILE = BASE_DIR / "project_registry.104a.bejson"

HISTORY_FIELDS = [
    {"name": "timestamp", "type": "string"},
    {"name": "project_name", "type": "string"},
    {"name": "version", "type": "string"},
    {"name": "file_path", "type": "string"}
]

REGISTRY_FIELDS = [
    {"name": "project_name", "type": "string"},
    {"name": "original_path", "type": "string"},
    {"name": "last_chunked", "type": "string"}
]

# Standard configuration defaults
DEFAULT_CONFIG = {
    "extensions": Utility.DEFAULT_EXTENSIONS,
    "exclude_dirs": Utility.DEFAULT_EXCLUDES,
    "evade_mime": True
}

def get_timestamp():
    return Utility.bejson_utility_get_timestamp()

def get_next_version(project_root):
    if not project_root.exists():
        return "v1"
    versions = []
    for d in project_root.iterdir():
        if d.is_dir() and d.name.startswith("v"):
            try:
                versions.append(int(d.name[1:]))
            except: pass
    if not versions:
        return "v1"
    return f"v{max(versions) + 1}"

def save_to_registry(project_name, original_path):
    registry = []
    if REGISTRY_FILE.exists():
        try:
            doc = BEJSONCore.bejson_core_load_file(str(REGISTRY_FILE))
            registry = doc.get("Values", [])
        except: pass
    
    # Check if exists, update path if changed
    found = False
    for i, row in enumerate(registry):
        if row[0] == project_name:
            registry[i][1] = str(original_path)
            registry[i][2] = get_timestamp()
            found = True
            break
    
    if not found:
        registry.append([project_name, str(original_path), get_timestamp()])
    
    doc = BEJSONCore.bejson_core_create_104a("ProjectRegistry", REGISTRY_FIELDS, registry)
    BEJSONCore.bejson_core_atomic_write(str(REGISTRY_FILE), doc)

def save_to_history(project_name, version, file_path):
    history = []
    if HISTORY_FILE.exists():
        try:
            doc = BEJSONCore.bejson_core_load_file(str(HISTORY_FILE))
            history = doc.get("Values", [])
        except: pass
    
    # Newest at top
    history.insert(0, [get_timestamp(), project_name, version, str(file_path)])
    history = history[:100] # Keep last 100
    
    doc = BEJSONCore.bejson_core_create_104a("ChunkHistory", HISTORY_FIELDS, history)
    BEJSONCore.bejson_core_atomic_write(str(HISTORY_FILE), doc)

def list_chunk_index():
    if not REGISTRY_FILE.exists():
        print("No project registry found.")
        return
    
    try:
        doc = BEJSONCore.bejson_core_load_file(str(REGISTRY_FILE))
        values = doc.get("Values", [])
        if not values:
            print("Registry is empty.")
            return
            
        print(f"\n{'ID':<4} | {'Project Name':<25} | {'Source Path'}")
        print("-" * 100)
        for i, row in enumerate(values, 1):
            name, path, _ = row
            print(f"{i:<4} | {name:<25} | {path}")
    except Exception as e:
        print(f"Error reading registry: {e}")

def list_unchunk_index():
    if not HISTORY_FILE.exists():
        print("No chunk history found.")
        return
    
    try:
        doc = BEJSONCore.bejson_core_load_file(str(HISTORY_FILE))
        values = doc.get("Values", [])
        if not values:
            print("History is empty.")
            return
            
        print(f"\n{'ID':<4} | {'Timestamp':<20} | {'Project':<20} | {'Ver':<6} | {'Chunk Path'}")
        print("-" * 120)
        for i, row in enumerate(values, 1):
            if len(row) == 4:
                ts, proj, ver, path = row
            else:
                ts, proj, path = row
                ver = "legacy"
            print(f"{i:<4} | {ts:<20} | {proj:<20} | {ver:<6} | {path}")
    except Exception as e:
        print(f"Error reading history: {e}")

def resolve_registry_id(index_str):
    if not REGISTRY_FILE.exists(): return None
    try:
        idx = int(index_str) - 1
        doc = BEJSONCore.bejson_core_load_file(str(REGISTRY_FILE))
        values = doc.get("Values", [])
        if 0 <= idx < len(values):
            return values[idx][0] # Index 0 is project_name
    except: pass
    return None

def resolve_registry_path(index_str):
    if not REGISTRY_FILE.exists(): return None
    try:
        idx = int(index_str) - 1
        doc = BEJSONCore.bejson_core_load_file(str(REGISTRY_FILE))
        values = doc.get("Values", [])
        if 0 <= idx < len(values):
            return values[idx][1] # Index 1 is original_path
    except: pass
    return None

def resolve_history_path(index_str):
    if not HISTORY_FILE.exists(): return None
    try:
        idx = int(index_str) - 1
        doc = BEJSONCore.bejson_core_load_file(str(HISTORY_FILE))
        values = doc.get("Values", [])
        if 0 <= idx < len(values):
            return values[idx][-1] # File path is always the last element
    except: pass
    return None

def expell_project(index_str):
    if not REGISTRY_FILE.exists():
        print("Error: No project registry found.")
        return
    
    try:
        idx = int(index_str) - 1
        doc = BEJSONCore.bejson_core_load_file(str(REGISTRY_FILE))
        values = doc.get("Values", [])
        
        if 0 <= idx < len(values):
            removed = values.pop(idx)
            print(f"[*] Expelling project: {removed[0]} (Registry entry removed, files preserved)")
            
            doc = BEJSONCore.bejson_core_create_104a("ProjectRegistry", REGISTRY_FIELDS, values)
            BEJSONCore.bejson_core_atomic_write(str(REGISTRY_FILE), doc)
        else:
            print(f"Error: Project ID {index_str} not found.")
    except Exception as e:
        print(f"Error expelling project: {e}")

def delete_project(index_str):
    if not REGISTRY_FILE.exists():
        print("Error: No project registry found.")
        return
    
    try:
        idx = int(index_str) - 1
        doc = BEJSONCore.bejson_core_load_file(str(REGISTRY_FILE))
        values = doc.get("Values", [])
        
        if 0 <= idx < len(values):
            removed = values.pop(idx)
            project_name = removed[0]
            print(f"[*] Deleting project: {project_name}")
            
            # Remove from registry
            doc = BEJSONCore.bejson_core_create_104a("ProjectRegistry", REGISTRY_FIELDS, values)
            BEJSONCore.bejson_core_atomic_write(str(REGISTRY_FILE), doc)
            
            # Delete project folder
            project_root = PROJECTS_DIR / project_name
            if project_root.exists():
                shutil.rmtree(project_root)
                print(f"[*] Deleted project files at {project_root}")
            else:
                print(f"Warning: Project folder not found at {project_root}")
        else:
            print(f"Error: Project ID {index_str} not found.")
    except Exception as e:
        print(f"Error deleting project: {e}")

def get_versions(index_str):
    project_name = resolve_registry_id(index_str)
    if not project_name:
        print(f"Error: Project ID {index_str} not found.")
        return
    
    project_root = PROJECTS_DIR / project_name
    if not project_root.exists():
        print(f"No versioned files found for project: {project_name}")
        return
    
    versions = sorted([d.name for d in project_root.iterdir() if d.is_dir() and d.name.startswith("v")], 
                      key=lambda x: int(x[1:]) if x[1:].isdigit() else 0)
    
    if not versions:
        print(f"No versions found for {project_name}")
        return
        
    print(f"\nVersions for project: {project_name}")
    print("-" * 30)
    for v in versions:
        print(f"  - {v}")

def delete_version(index_str, version_str):
    project_name = resolve_registry_id(index_str)
    if not project_name:
        print(f"Error: Project ID {index_str} not found.")
        return
    
    version_dir = PROJECTS_DIR / project_name / version_str
    if version_dir.exists() and version_dir.is_dir():
        print(f"[*] Deleting version {version_str} for project {project_name}...")
        shutil.rmtree(version_dir)
        print("[*] Success.")
    else:
        print(f"Error: Version {version_str} not found for project {project_name} at {version_dir}")

def run_chunk(target_dir):
    target_path = Path(target_dir).resolve()
    if not target_path.is_dir():
        print(f"Error: {target_dir} is not a directory.")
        return

    # Project identification
    project_name = target_path.name.replace(" ", "_")
    project_root = PROJECTS_DIR / project_name
    version = get_next_version(project_root)
    version_dir = project_root / version
    version_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Mode: CHUNK (104db)")
    print(f"[*] Project: {project_name} ({version})")
    print(f"[*] Target: {target_path}")
    
    doc = Utility.bejson_utility_create_cli_chunk(
        target_dir=str(target_path),
        project_name=project_name,
        version=version
    )
    
    # Structural Validation
    print("[*] Validating BEJSON structure...")
    res = Validator.validate_bejson(doc)
    if not res.valid:
        print("\n[ERROR] BEJSON Validation Failed:")
        for err in res.errors:
            print(f"  - {err}")
        return

    ext = ".104db.bejson"
    if DEFAULT_CONFIG.get("evade_mime"):
        ext += ".txt"
        
    out_file = version_dir / f'Chunked_{Utility.bejson_utility_sanitize_name(project_name)}_{version}{ext}'
    
    if Utility.bejson_utility_save_chunk(str(out_file), doc):
        print(f"\n[SUCCESS] Project chunked into {out_file}")
        print(f"[*] Total Records: {len(doc['Values'])}")
        save_to_registry(project_name, target_path)
        save_to_history(project_name, version, out_file)
    else:
        print(f"\n[ERROR] Failed to save BEJSON chunk.")

def run_unchunk(bejson_file, destination=None):
    input_path = Path(bejson_file).resolve()
    if not input_path.exists():
        print(f"Error: File {bejson_file} not found.")
        return

    print(f"[*] Mode: UNCHUNK")
    print(f"[*] Source: {input_path}")
    
    try:
        # Structural Validation
        print("[*] Validating BEJSON structure...")
        res = Validator.validate_bejson(str(input_path), is_file=True)
        if not res.valid:
            print("\n[ERROR] BEJSON Validation Failed:")
            for err in res.errors:
                print(f"  - {err}")
            return

        doc = BEJSONCore.bejson_core_load_file(str(input_path))
        if doc.get("Format_Version") != "104db":
            print("Error: Input is not a valid BEJSON 104db file.")
            return

        # Mapping indices based on field schema
        fields = [f["name"] for f in doc["Fields"]]
        pname_idx = fields.index("project_name")
        fpath_idx = fields.index("file_path")
        cont_idx = fields.index("content")
        bin_idx = fields.index("is_binary")
        
        # Manually filter records by type (104db discriminator is index 0)
        meta_rows = [r for r in doc["Values"] if r[0] == "ProjectMeta"]
        proj_name = meta_rows[0][pname_idx] if meta_rows else "RestoredProject"
        
        # Setup Output Dir
        if destination:
            out_dir = Path(destination).resolve()
        else:
            ts_slug = get_timestamp().replace(":", "").replace("-", "")
            out_dir = Path.cwd() / "Restored_Projects" / proj_name / ts_slug
        
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract Files
        file_rows = [r for r in doc["Values"] if r[0] == "FileContent"]
        for row in file_rows:
            rel_path = row[fpath_idx]
            content = row[cont_idx]
            binary = row[bin_idx]
            
            if rel_path:
                target_file = out_dir / rel_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                if binary:
                    target_file.touch()
                else:
                    target_file.write_text(content, encoding="utf-8")
                print(f"  [>] {rel_path}")

        print(f"\n[SUCCESS] Project rebuilt at {out_dir}")

    except Exception as e:
        print(f"\n[ERROR] Unchunking failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="BEJSON Project Chunker/Unchunker - Indexed System")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--chunk", metavar="DIR", help="Chunk a directory into BEJSON")
    group.add_argument("--chunk-index", metavar="ID", help="Chunk a registered project by numeric ID")
    group.add_argument("--unchunk", metavar="FILE", help="Unchunk a BEJSON file")
    group.add_argument("--unchunk-index", metavar="ID", help="Unchunk a historical chunk by numeric ID")
    group.add_argument("--list-chunk-index", action="store_true", help="List all registered projects")
    group.add_argument("--list-project-index", action="store_true", help="Alias for --list-chunk-index")
    group.add_argument("--list-unchunk-index", action="store_true", help="List all historical chunks with numeric IDs")
    group.add_argument("--expell-project", metavar="ID", help="Remove a project from the registry (files kept)")
    group.add_argument("--delete-project", metavar="ID", help="Remove a project and delete all its chunk files")
    group.add_argument("--get-versions", metavar="ID", help="List all available versions for a project ID")
    group.add_argument("--delete-version", nargs=2, metavar=("ID", "VER"), help="Delete a specific version (e.g., v1) for a project ID")
    
    parser.add_argument("--dest", metavar="DIR", help="Custom destination for unchunking")
    
    args = parser.parse_args()
    
    if args.list_chunk_index or args.list_project_index:
        list_chunk_index()
    elif args.list_unchunk_index:
        list_unchunk_index()
    elif args.chunk:
        run_chunk(args.chunk)
    elif args.chunk_index:
        source_path = resolve_registry_path(args.chunk_index)
        if source_path:
            run_chunk(source_path)
        else:
            print(f"Error: Project ID {args.chunk_index} not found in registry.")
    elif args.unchunk:
        run_unchunk(args.unchunk, args.dest)
    elif args.unchunk_index:
        chunk_path = resolve_history_path(args.unchunk_index)
        if chunk_path:
            run_unchunk(chunk_path, args.dest)
        else:
            print(f"Error: Chunk ID {args.unchunk_index} not found in history.")
    elif args.expell_project:
        expell_project(args.expell_project)
    elif args.delete_project:
        delete_project(args.delete_project)
    elif args.get_versions:
        get_versions(args.get_versions)
    elif args.delete_version:
        delete_version(args.delete_version[0], args.delete_version[1])

if __name__ == "__main__":
    main()
