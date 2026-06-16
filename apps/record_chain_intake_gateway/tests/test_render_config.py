"""Tests for render.yaml deployment configuration."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

RENDER_YAML = Path(__file__).resolve().parents[1] / "render.yaml"


class TestRenderConfig:
    def test_render_yaml_exists(self):
        assert RENDER_YAML.exists(), "render.yaml not found"

    def test_render_yaml_has_service(self):
        data = yaml.safe_load(RENDER_YAML.read_text())
        services = data.get("services", [])
        assert len(services) > 0
        svc = services[0]
        assert svc.get("type") == "web_service"

    def test_has_safe_build_command(self):
        data = yaml.safe_load(RENDER_YAML.read_text())
        svc = data["services"][0]
        build = svc.get("buildCommand", "")
        start = svc.get("startCommand", "")
        # Either rootDir or repo-root-safe commands
        has_root_dir = "rootDir" in svc
        has_safe_build = "apps/record_chain_intake_gateway" in build or "requirements.txt" in build
        has_safe_start = "apps.record_chain_intake_gateway" in start or "app:app" in start
        assert has_root_dir or (has_safe_build and has_safe_start), \
            "render.yaml must use rootDir or repo-root-safe commands"

    def test_has_required_env_vars(self):
        data = yaml.safe_load(RENDER_YAML.read_text())
        svc = data["services"][0]
        env_vars = {e["key"] for e in svc.get("envVars", [])}
        required = {"TRINITY_REPO_FULL_NAME", "TRINITY_TARGET_BRANCH", "TRINITY_GITHUB_TOKEN"}
        assert required.issubset(env_vars), f"Missing env vars: {required - env_vars}"
