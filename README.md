# BlockAccred
**Blockchain-Based Transparent and Tamper-Evident Accreditation Evidence Verification System**

> **Academic Prototype — Not an Official NBA System.**
> All institution, student, faculty and evidence data in this project is fictional demo data created for a
> college project demonstration. This is not connected to the National Board of Accreditation and does not
> submit, store, or affect any real accreditation record.

Evidence Submission → SHA-256 Hash → Blockchain Record → Verification → Audit Trail

---

## What's in this project

```
BlockAccred/
├── backend/        FastAPI + SQLite (SQLAlchemy) API, SHA-256 hashing, blockchain client, ML wrapper
├── blockchain/      Solidity contract + Hardhat local blockchain
├── ml/               Isolation Forest anomaly detection (trained on demo historical data)
├── frontend/         React + Vite web app
└── demo_documents/   A sample PDF you can edit to demonstrate tamper detection
```

## 1. Prerequisites

- Python 3.10+
- Node.js 18+
- Optional: PostgreSQL only if you want to switch away from the default local SQLite setup

For the default local prototype run, no external database server is required.

## 2. Start the local blockchain (terminal 1)

```bash
cd blockchain
npm install
npx hardhat node
```

Leave this running. It prints 20 demo accounts — this is your local, throwaway blockchain.

## 3. Deploy the smart contract (terminal 2, one-time per node restart)

```bash
cd blockchain
npx hardhat run scripts/deploy.js --network localhost
```

This writes `blockchain/deployment.json` (contract address + ABI), which the backend reads automatically.
**Whenever you restart `npx hardhat node`, re-run this deploy step** — a fresh local chain has no contract on it yet.

## 4. Set up the backend (terminal 3)

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
python seed.py                # creates demo users, institution, programme, and 20 evidence records
uvicorn app.main:app --reload
```

The default configuration uses a local SQLite database file in the backend folder, which is easier for a prototype and works without needing a separate PostgreSQL service.

For deployment, switch the backend to a hosted PostgreSQL database and a public blockchain RPC by editing the values in `.env`.

## Deploy to Render

The root `render.yaml` defines the React static site, FastAPI service, PostgreSQL database, and a persistent disk for uploaded evidence. The web-service disk and paid PostgreSQL plan have a cost; review Render's current pricing before creating the Blueprint.

1. Push this project to a GitHub repository.
2. In `blockchain`, copy `.env.example` to `.env`, set `BLOCKCHAIN_RPC_URL` and `BLOCKCHAIN_PRIVATE_KEY`, then deploy the contract to Sepolia. Use a dedicated test wallet, never a wallet holding real funds, and fund it with Sepolia test ETH first.

```bash
cd blockchain
npm install
npx hardhat run scripts/deploy.js --network sepolia
```

3. Create a new Blueprint in the Render Dashboard using the GitHub repository. When prompted, enter the same `BLOCKCHAIN_RPC_URL` and `BLOCKCHAIN_PRIVATE_KEY`, plus the deployed address as `CONTRACT_ADDRESS`. The private key must be the owner of the deployed contract. The Render API uses the bundled ABI, so the ignored local `deployment.json` is not needed. Keep `.env` files and private keys out of Git.

The Blueprint uses the default Render URLs `https://blockaccred.onrender.com` and `https://blockaccred-api.onrender.com`. If Render assigns different URLs, update the frontend's `VITE_API_URL` and the API's `CORS_ORIGINS` in the Render Dashboard, then redeploy the frontend.

After the API and Sepolia contract are available, open the backend service Shell in Render and run `python seed.py` once to create the demo users and records. The seed submits blockchain transactions and therefore requires a funded test wallet. The demo logins below are not created automatically by deployment.

The static frontend can take API requests, but the SQLite file and local Hardhat node are for local development only. Render uses managed PostgreSQL, a persistent disk for uploaded documents, and Sepolia for blockchain writes.

For local container development, `docker-compose up --build` remains available.

The API is now at `http://localhost:8000` (interactive docs at `http://localhost:8000/docs`).

`seed.py` submits each demo evidence record through the real evidence workflow, so it also creates 20 real
transactions on your local blockchain — make sure steps 2 and 3 are done first, or it will stop with an error
telling you so.

## 5. Set up the frontend (terminal 4)

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` and log in.

## Demo login accounts

| Role          | Email                    | Password     |
|---------------|--------------------------|---------------|
| College Admin | admin@college.com        | admin123      |
| Reviewer      | reviewer@nba-demo.com    | reviewer123   |
| Student       | student@college.com      | student123    |

These are fictional accounts created only for demonstration.

## 6. The main demonstration (tamper detection)

1. Log in as **College Admin** → **Submit Evidence**.
2. Parameter: `Placement`, claimed value `85`, upload `demo_documents/placement_report.pdf`.
3. The system computes the SHA-256 hash and records it on the local blockchain — you'll see the Evidence ID,
   hash, version and transaction hash immediately.
4. Log in as **Reviewer** → **Reviewer Queue** → open the record → **Verify evidence**.
5. Make a copy of `demo_documents/placement_report.pdf`, open it in any text/PDF editor, and change some text
   (e.g. `85%` → `99%`). Save it as a new file.
6. Back in the app, open the evidence record → **Integrity Check** → upload the modified file.
7. The app shows **❌ Hash Mismatch — Document Modified**, because the current file's hash no longer matches
   the hash recorded on the blockchain when the evidence was first submitted.
8. Open **Audit Trail** to show every step chronologically, and **Anomalies** to show the ML model flagging
   the unusually high placement value used in the demo seed data.

## Notes

- Documents are stored locally in `backend/uploads/`; only their SHA-256 hash is ever written to the blockchain.
- Evidence versions are never overwritten — each new submission creates a new version with its own hash.
- "Prototype Assessment Score" and the five prototype parameters are demonstration constructs only, not
  official NBA criteria or scoring rules.
- The anomaly detector only flags statistically unusual values for review; it never asserts fraud or
  manipulation.
