import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import { apiGet } from "../api";

export default function Payout(){
  const loc = useLocation();
  const result = loc.state?.result;
  const [txStatus, setTxStatus] = useState(null);

  if(!result) return <div className="card"><h3>No result</h3></div>;

  const insuredAmount = 1000;
  const amount = Math.round((insuredAmount * (result.payout_percentage||0))/100*100)/100;

  async function checkOnchain(){
    if(!result.claim_id) return;
    const r = await apiGet(`/api/claims/${result.claim_id}/tx_status`);
    setTxStatus(r);
  }

  const explorer = result.onchain?.tx_hash ? `https://sepolia.etherscan.io/tx/${result.onchain.tx_hash}` : null;

  return (
    <div className="card">
      <h2>Payout</h2>
      <p>Claim ID: {result.claim_id}</p>
      <p>Is stressed: {result.is_stressed? 'Yes':'No'}</p>
      <p>Probability: {result.probability}</p>
      <p>Payout %: {result.payout_percentage}%</p>
      <p>Claimable amount (demo insured {insuredAmount}): {amount}</p>

      {explorer && <p>On-chain tx: <a target="_blank" href={explorer} rel="noreferrer">{result.onchain.tx_hash}</a></p>}
      <div>
        <button onClick={checkOnchain}>Check On-chain Status</button>
        <pre>{txStatus ? JSON.stringify(txStatus, null, 2) : "No status yet"}</pre>
      </div>
    </div>
  );
}
