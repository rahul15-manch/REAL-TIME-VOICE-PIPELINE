# AWS EC2 Production Deployment Guide

This document defines the infrastructure and deployment procedure for hosting the realtime-voice-pipeline Docker container on AWS EC2.

## 1. AWS Region
- **Region:** `us-east-1` (or another appropriate region closest to users to minimize audio latency).

## 2. EC2 Instance Type
- **Instance Type:** `t3.medium` or `t3.large`.
- **Reasoning:** 2 vCPU and 4 GB RAM minimum is required to run the Docker daemon, 4 Uvicorn workers, and handle multiple WebSocket streams (Pipecat + LiveKit/Twilio).
- **Storage:** 30 GB EBS gp3 volume.

## 3. AMI (Amazon Machine Image)
- **AMI:** Ubuntu Server 22.04 LTS (HVM), SSD Volume Type
- **Architecture:** `x86_64` (Standard Pipecat/WebRTC dependencies compile reliably on x86).

## 4. VPC
- **VPC:** Deploy into an existing custom VPC or Default VPC.
- **Requirement:** The VPC must have an Internet Gateway attached to allow the container to reach external provider APIs (OpenAI, Deepgram, Cartesia, Twilio, Neon DB).

## 5. Subnet
- **Subnet:** A public subnet (if hosting Twilio Webhook endpoints directly) OR a private subnet behind an ALB (Milestone 4). For this milestone, a public subnet with an auto-assigned public IPv4 is assumed for direct testing.

## 6. Security Group
- **Inbound Rules:**
  - `SSH (TCP 22)`: Source = `Administrator IP / CIDR` (Least privilege, NEVER `0.0.0.0/0`).
  - `Custom TCP (TCP 8000)`: Source = `Administrator IP / CIDR` (Temporary for M3 direct testing. Will be replaced by ALB in M4).
- **Outbound Rules:**
  - All Traffic (`0.0.0.0/0`) -> Needed for Deepgram, OpenAI, Cartesia, and PostgreSQL connectivity.

## 7. IAM Role
- **Instance Profile Name:** `VoicePipelineEC2Role`
- **Permissions:** 
  - `SecretsManagerReadWrite` (Scope strictly down to the `VoicePipelineSecrets` ARN).
  - *No Administrator access. No unnecessary S3/EC2 modification rights.*

## 8. Docker Installation
Run on the EC2 instance:
```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker ubuntu
sudo systemctl enable docker
```

## 9. Repository Deployment
```bash
# Clone the repository securely
git clone https://github.com/rahul15-manch/REAL-TIME-VOICE-PIPELINE.git
cd REAL-TIME-VOICE-PIPELINE
```

## 10. Image Build
```bash
# Build the production image locally on EC2 (or pull from ECR if configured)
docker build -t realtime-voice-pipeline:latest .
```

## 11. Secret Injection
Use AWS CLI to fetch secrets securely without committing `.env`:
```bash
# Fetch from Secrets Manager and write to an ephemeral .env file used strictly by docker-compose
aws secretsmanager get-secret-value --secret-id VoicePipelineProd --query SecretString --output text > .env
```

## 12. Container Startup
```bash
# Start the container natively using the 4 Uvicorn workers configuration
docker compose up -d
```

## 13. Health Checks
```bash
# Verify container is running and port 8000 is open
docker ps
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

## 14. Database Connectivity
The application will internally connect to the Neon Postgres deployment. You can verify this by checking the container logs for `Database schemas created/verified successfully`:
```bash
docker compose logs voice-pipeline
```

## 15. Reboot Recovery
- Ensure Docker starts on boot (`sudo systemctl enable docker`).
- The `docker-compose.yml` uses `restart: unless-stopped`, so the container will automatically resurrect upon instance reboot, instantly hooking back into the Database and WebSockets.

## 16. Rollback Procedure
If a new image fails on EC2:
1. Stop the failing container: `docker compose down`
2. Revert the Git repository to the previous stable commit: `git checkout <previous_commit_hash>`
3. Rebuild the image: `docker build -t realtime-voice-pipeline:latest .`
4. Start the container: `docker compose up -d`
5. Verify health: `curl http://localhost:8000/health`
6. Verify database connectivity: `docker compose logs voice-pipeline | grep "Database"`

---
**Note:** No SSL/TLS or domain routing is configured in this document. Production HTTPS and WSS (WebSockets over SSL) will be handled via an Application Load Balancer in Milestone 4.
