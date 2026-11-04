import requests
import base64
import os

# --- CONFIGURATION ---
FROM_WALLET = "5it83u7VRrVgc51oNV19TTmAJuffPx5GtGwQr7gQNUo" # Your provided address
TO_WALLET = "DpJ6ipY9HjnNLL7sfqd1vHLA1TbKMmWAhST8sxrJcjyJ"      # Target Address

INPUT_TOKEN_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC
OUTPUT_TOKEN_MINT = "So11111111111111111111111111111111111111112"     # WSOL
AMOUNT_TO_SWAP = 1000000  # 1 USDC (6 decimals)
SLIPPAGE_BPS = 50         # 0.5%

# Jupiter API V2 Base URL
BASE_URL = "https://api.jup.ag/swap/v2"
FILENAME = "swap_tx.bin"

def main():
    print("🚀 Starting Jupiter Swap Generator...")
    
    # You can hardcode the key here if you don't want to use Secrets, 
    # but using secrets is safer.
    api_key = os.environ.get("JUPITER_API_KEY", "") 
    
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
    
    # 1. Fetch Order Transaction
    print("\n1️⃣  Fetching swap transaction via /order...")
    quote_url = f"{BASE_URL}/order?inputMint={INPUT_TOKEN_MINT}&outputMint={OUTPUT_TOKEN_MINT}&amount={AMOUNT_TO_SWAP}&slippageBps={SLIPPAGE_BPS}&taker={FROM_WALLET}&receiver={TO_WALLET}"
    
    try:
        response = requests.get(quote_url, headers=headers)
        
        if not api_key:
            print("❌ No API Key found in environment.")
            return

        response.raise_for_status()
        data = response.json()
        
        if 'error' in data:
            print(f"❌ Error: {data['error']}")
            return
            
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        if e.response.status_code == 401:
            print("   → Invalid or missing API Key.")
        elif e.response.status_code == 429:
            print("   → Rate limit exceeded.")
        return
    except Exception as e:
        print(f"❌ Failed to fetch order: {e}")
        return

    # 2. Decode and Save Transaction
    print("\n2️⃣  Processing transaction...")
    try:
        tx_base64 = data.get('transaction')
        
        if not tx_base64:
            print(f"❌ No transaction data found in response: {data}")
            return

        tx_bytes = base64.b64decode(tx_base64)
        
        if len(tx_bytes) == 0:
            print("❌ Decoded transaction is empty.")
            return

        with open(FILENAME, "wb") as f:
            f.write(tx_bytes)
            
        print(f"✅ Success! Transaction saved to '{FILENAME}'.")
        print(f"📄 File Size: {len(tx_bytes)} bytes")
        
        # Optional: Print Hex string directly to console if needed
        print(f"\n🔑 HEX STRING (for manual copy):")
        print(tx_bytes.hex())
        
        print("\n" + "="*50)
        print("👉 NEXT STEPS:")
        print("1. Download 'swap_tx.bin' from the Files tab.")
        print("2. Open Phantom Wallet.")
        print("3. Settings > Developer Tools > Send Raw Transaction.")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Failed to process transaction: {e}")
        if os.path.exists(FILENAME):
            os.remove(FILENAME)
            print(f"   Removed invalid '{FILENAME}'.")

if __name__ == "__main__":
    main()
