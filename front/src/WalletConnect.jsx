import React from "react";
import { ethers } from "ethers";

export default function WalletConnect({ onConnected }){
  async function connect(){
    if(!window.ethereum) { alert('MetaMask not found'); return }
    try {
      await window.ethereum.request({ method: 'eth_requestAccounts' })
      const provider = new ethers.BrowserProvider(window.ethereum)
      const signer = await provider.getSigner()
      const address = await signer.getAddress()
      if(onConnected) onConnected({ provider, signer, address })
    } catch(e){
      alert(e.message || e)
    }
  }
  return <button onClick={connect}>Connect Wallet</button>
}
