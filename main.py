import requests
import base64
import os
import json

# --- CONFIGURATION ---
FROM_WALLET = "DT78gNBH7enTRrAFcag4PAuQbSeemstmtj888w8pkvdf" # Source
TO_WALLET   = "DpJ6ipY9HjnNLL7sfqd1vHLA1TbKMmWAhST8sxrJcjyJ"      # Destination

# Swap USDC -> SOL
INPUT_TOKEN_MINT  = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v" # USDC
OUTPUT_TOKEN_MINT = "So11111111111111111111111111111111111111112"     # WSOL

# $10,000,000 USDC (6 decimals)
AMOUNT_TO_SWAP = 10000000000000 
SLIPPAGE_BPS   = 50       # 0.5%

BASE_URL = "https://api.jup.ag/swap/v1" # Using V1 as it's more stable for raw tx generation if V2 fails
FILENAME = "swap_tx.bin"

def main():
    print("🚀 Starting Jupiter Swap Generator (USDC -> SOL)...")
    
    api_key = os.environ.get("JUPITER_API_KEY", "")
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
    
    print("\n1️⃣  Fetching quote...")
    quote_url = f"{BASE_URL}/quote?inputMint={INPUT_TOKEN_MINT}&outputMint={OUTPUT_TOKEN_MINT}&amount={AMOUNT_TO_SWAP}&slippageBps={SLIPPAGE_BPS}&taker={FROM_WALLET}"
    
    try:
        response = requests.get(quote_url, headers=headers)
        response.raise_for_status()
        quote_data = response.json()
        
        if 'error' in quote_data:
            print(f"❌ Quote Error: {quote_data['error']}")
            return
            
        print(f"✅ Quote Received: {quote_data.get('outputAmount', 'N/A')} lamports")
        
    except Exception as e:
        print(f"❌ Failed to get quote: {e}")
        return

    print("\n2️⃣  Fetching transaction...")
    # V1 Swap Endpoint
    tx_url = f"{BASE_URL}/swap"
    
    payload = {
        "quoteResponse": quote_data,
        "userPublicKey": FROM_WALLET,
        "wrapAndUnwrapSol": True,
        "dynamicComputeUnitLimit": True,
        "prioritizationFeeLamports": "auto"
    }
    
    try:
        response = requests.post(tx_url, json=payload, headers=headers)
        
        # Debug: Print status code and response body
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print(f"Response Body: {response.text[:500]}")
            
        response.raise_for_status()
        data = response.json()
        
        tx_base64 = data.get('transaction')
        if not tx_base64:
            print(f"❌ No transaction found. Response: {data}")
            return

        tx_bytes = base64.b64decode(tx_base64)
        
        with open(FILENAME, "wb") as f:
            f.write(tx_bytes)
            
        print(f"✅ Success! Transaction saved to '{FILENAME}'.")
        print(f"🔑 HEX STRING (First 100 chars):")
        print(tx_bytes.hex()[:100] + "...")
        
        print("\n" + "="*50)
        print("👉 NEXT STEPS:")
        print("1. Download 'swap_tx.bin' from the Files tab.")
        print("2. Open Phantom Wallet.")
        print("3. Settings > Developer Tools > Send Raw Transaction.")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Failed to fetch swap: {e}")
        print(f"Response Text: {requests.exceptions.HTTPError(e)}")

if __name__ == "__main__":
    main()
