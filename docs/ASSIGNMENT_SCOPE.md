# Submission scope update - 2026-10-22

This is a student-supplied clarification, not an edit to the instructor's original README.
The student confirmed that domain, HTTPS and independent reverse-proxy authentication
requirements are cancelled. Tasks 1 and 2 continue: local deployment, improved essay
instructions, Docker image distribution through ACR, ECS deployment and evidence.
No revised allocation of marks has been supplied; do not invent one.

Required deliverables retained:
- A report of no more than 20 pages, produced using AI Learning Assistant and reviewed.
- The student's whole-project GitHub repository URL, including revised essay instructions.
- Original `local-ui-check.txt` and `ecs-docker-check.txt` files.
- Local and ECS interface screenshots with visible browser address bars in the report.

Task 3 is NOT REQUIRED under this clarified scope. Do not claim TLS, Nginx or a domain
was configured. Direct HTTP remains a teaching-only setup; restrict TCP 14242 to the
student's public IP. The application's BNBU login is not production-grade security.

Historical evidence (2026-10-14) records local HTTP 200, a healthy ECS container and
successful ECS loopback `/health`. ECS self-access via its public IP timed out (curl
28, HTTP 000). Retain that result; it does not establish the cause of the timeout.
The student separately supplied a browser screenshot showing the ECS public URL and
a successful generation. Reattach its original image to the final report.

The 2026-10-22 prompt revision is a source change. The existing ECS `ba3073-v1`
image predates it; do not claim the cloud image contains this revision until rebuilt
and redeployed. An explicit updated task brief can also communicate the revised scope
to the deployed app when generating a report.
