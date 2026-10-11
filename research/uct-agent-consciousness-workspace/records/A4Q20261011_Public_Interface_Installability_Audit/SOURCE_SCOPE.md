# A4Q source scope

## Fixed project sources read

- `RESEARCH_MASTER_GUIDE.md`, `AGENTS.md`, latest `MEMORY.md`, `HANDOFF.md`, `MASTER_INDEX.md`, A4P handoff/round record, `REVIEW_SUPERVISION.md`, `UCT_FORMAL_MAP.md`, `UCT_FORMAL_GRAPH.json` and `UCT_FORMAL_AUDIT.md`.
- UCT I v1.2 §§8.11–8.14 and 14.3–14.10 from `records/R128_Unified_Formal_Map_Audit_20261006/sources/A_UCT_I_v1_2.md`, pinned SHA256 `2e4469afbd1d1862463cc36396dd6e2b50c418f22d6f0fd584bbae33bfedc6f4`.
- R159 §§1–9, effective R173 map objects, A4D–A4G protocols, and A4P's `INTERVENTION_CONTRACT.md`, research note, exact results, gaps and formal audit.
- Effective map restored locally from `integration/UCT-INTEGRATION-v1.0.0/restore_unified_map.py`: 913 nodes, 424 active rules, 261 context links; 727 pending objects remain disabled and 10 historical rules remain suspended.

## Official public interface sources inspected

Retrieved 2026-10-11; URLs are recorded because the documentation is mutable.

1. Universal Robots, **Real-Time Data Exchange (RTDE) Guide**: https://docs.universal-robots.com/tutorials/communication-protocol-tutorials/rtde-guide.html
2. Universal Robots, **UR Client Library architecture**: https://docs.universal-robots.com/Universal_Robots_ROS2_Documentation/doc/ur_client_library/doc/architecture.html
3. UniversalRobots, **ReverseInterface architecture/source documentation**: https://github.com/UniversalRobots/Universal_Robots_Client_Library/blob/master/doc/architecture/reverse_interface.rst
4. Universal Robots, **ROS 2 driver controllers**: https://docs.universal-robots.com/Universal_Robots_ROS2_Documentation/doc/ur_robot_driver/ur_robot_driver/doc/usage/controllers.html
5. Universal Robots, **Utility controllers**: https://docs.universal-robots.com/Universal_Robots_ROS_Documentation/rolling/doc/ur_robot_driver/ur_robot_driver/doc/usage/utility_controllers.html
6. Universal Robots, **Position and velocity control**: https://docs.universal-robots.com/Universal_Robots_ROS_Documentation/rolling/doc/ur_robot_driver/ur_robot_driver/doc/usage/position_velocity_control.html
7. Universal Robots, **Safety configuration**, SW10.15 manual: https://www.universal-robots.com/manuals/EN/HTML/SW10_15/Content/prod-usr-man/complianceG7/PolyX_SW/Safety.htm
8. UniversalRobots, **Universal Robots ROS 2 Driver repository**: https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver

## Evidence and inference boundary

The documents ground public field directions, nominal/exception timing behavior, controller resource claims, command modes and listed safety/control paths. They do not establish absence of every internal or vendor-only interface. The claim “no stock native anchor substitution port is documented” is a bounded inference from the inspected public interfaces, not a vendor quotation or a universal hardware impossibility claim.

No robot, firmware image, calibration, driver commit, controller graph, program, packet trace or external tracker was inspected. GitHub `master`/rolling pages were not pinned to a source commit in this round. Those omissions block actual installation and long-term reproducibility; a future experiment must vendor the exact source/docs and record hashes.

## Prior-art and originality boundary

RTDE, ROS 2 control, closed-loop feedback, intervention locality, block/rescue and controller-inventory methods are prior art. A4Q claims no new robotics protocol or causal theorem. The project-specific contribution is the typed route-grain audit against A4P and the explicit separation between an inaccessible native route and a prospectively instrumentable composite external route.
