import json
import time
import random
from web3 import Web3
from eth_account import Account

# Konfigurasi - EXACT dari transaksi sukses
RPC_URL = "https://soneium.drpc.org"
CHAIN_ID = 1868

# Inisialisasi Web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Contract address
CONTRACT_ADDRESS = "0x1e6d5018970F982Af9208AA10322c29e808cBC89"

def load_private_keys(filename="pk.txt"):
    """Memuat private keys dari file"""
    try:
        with open(filename, 'r') as f:
            keys = [line.strip() for line in f if line.strip()]
        return keys
    except FileNotFoundError:
        print(f"File {filename} tidak ditemukan!")
        return []

def send_exact_transaction(private_key, tx_number, total_tx, domain="bearstudio.zombie.ads", symbol="ETH"):
    """
    Send transaction dengan EXACT parameters dari tx sukses
    """
    try:
        account = Account.from_key(private_key)
        address = account.address

        print(f"\n{'='*60}")
        print(f"TX #{tx_number}/{total_tx} | Wallet: {address}")
        print(f"{'='*60}")

        # Check balance
        balance = w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance, 'ether')
        print(f"ðŸ’° Balance: {balance_eth:.9f} ETH")

        if balance_eth < 0.00015:
            print(f"âŒ Insufficient balance")
            return False

        # Get nonce
        nonce = w3.eth.get_transaction_count(address)
        print(f"ðŸ”¢ Nonce: {nonce}")

        # EXACT raw data dari tx sukses
        raw_data = "0xc63e529b0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000156265617273747564696f2e7a6f6d6269652e616473000000000000000000000000000000000000000000000000000000000000000000000000000000000000034554480000000000000000000000000000000000000000000000000000000000"
        
        print(f"ðŸ“ Domain: {domain} | Symbol: {symbol}")

        # EXACT gas parameters
        gas_limit = 67200
        value_wei = 1000000000000  # 0.000001 ETH
        
        # Get current base fee
        try:
            latest_block = w3.eth.get_block('latest')
            base_fee = latest_block.get('baseFeePerGas')
            
            if base_fee is None or base_fee == 0:
                base_fee = 33963
        except:
            base_fee = 33963

        # EXACT dari tx sukses
        max_priority_fee_per_gas = 1026000  # 0.001026 Gwei
        max_fee_per_gas = base_fee + 1078000  # base + 0.001078 Gwei
        
        print(f"â›½ Gas: {gas_limit:,} | Priority: {max_priority_fee_per_gas/1e9:.6f} Gwei | Max: {max_fee_per_gas/1e9:.6f} Gwei")

        # Build transaction
        transaction = {
            'from': address,
            'to': CONTRACT_ADDRESS,
            'value': value_wei,
            'gas': gas_limit,
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee_per_gas,
            'nonce': nonce,
            'chainId': CHAIN_ID,
            'type': 2,
            'data': raw_data
        }

        # Sign and send
        signed_txn = account.sign_transaction(transaction)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_hash_hex = tx_hash.hex()
        
        print(f"âœ… Sent! TX: {tx_hash_hex[:16]}...{tx_hash_hex[-8:]}")
        print(f"ðŸ”— https://soneium.blockscout.com/tx/{tx_hash_hex}")

        # Wait for confirmation
        print(f"â³ Waiting for confirmation...", end='', flush=True)
        
        try:
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash_hex, timeout=120)
            
            if receipt['status'] == 1:
                gas_used = receipt['gasUsed']
                
                # Calculate fees
                effective_gas_price = receipt.get('effectiveGasPrice', 0)
                
                # Handle l1Fee as hex string or int
                l1_fee_raw = receipt.get('l1Fee', 0)
                if isinstance(l1_fee_raw, str):
                    l1_fee = int(l1_fee_raw, 16) if l1_fee_raw.startswith('0x') else int(l1_fee_raw)
                else:
                    l1_fee = l1_fee_raw
                
                l2_fee = gas_used * effective_gas_price
                total_fee = l2_fee + l1_fee
                
                print(f" âœ… CONFIRMED!")
                print(f"ðŸ“¦ Block: {receipt['blockNumber']} | Gas: {gas_used:,} ({gas_used/gas_limit*100:.1f}%)")
                print(f"ðŸ’¸ Fee: {w3.from_wei(total_fee, 'ether'):.9f} ETH (L2: {w3.from_wei(l2_fee, 'ether'):.9f} + L1: {w3.from_wei(l1_fee, 'ether'):.9f})")
                print(f"âœ… SUCCESS!")
                return True
            else:
                print(f" âŒ FAILED")
                print(f"âŒ Status: {receipt['status']}")
                return False
                
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                print(f" â° TIMEOUT")
                print(f"âš ï¸ Check manually: https://soneium.blockscout.com/tx/{tx_hash_hex}")
                return True  # Assume success
            else:
                print(f" âŒ ERROR: {error_msg[:50]}")
                return False

    except Exception as e:
        error_msg = str(e).lower()
        
        if "insufficient funds" in error_msg:
            print(f"âŒ Insufficient funds")
        elif "nonce too low" in error_msg:
            print(f"âŒ Nonce too low")
        elif "already known" in error_msg:
            print(f"âš ï¸ Already in mempool (may succeed)")
            return True
        else:
            print(f"âŒ Error: {str(e)[:100]}")
        
        return False

def main():
    print("="*60)
    print("ðŸŽ¯ SONEIUM CLAIM BOT - MULTI TX MODE")
    print("="*60)

    # Connection check
    try:
        block = w3.eth.block_number
        chain_id = w3.eth.chain_id
        gas_price = w3.eth.gas_price
        
        print(f"\nâœ… Connected to Soneium Minato")
        print(f"   Chain ID: {chain_id}")
        print(f"   Block: {block:,}")
        print(f"   Gas: {gas_price/1e9:.6f} Gwei")
    except Exception as e:
        print(f"\nâŒ Connection failed: {e}")
        return

    # Load private keys
    private_keys = load_private_keys("pk.txt")
    
    if not private_keys:
        print("\nâŒ No private keys in pk.txt")
        return

    print(f"\nðŸ“‚ Loaded {len(private_keys)} wallet(s)")

    # Configuration
    print(f"\nâš™ï¸ Configuration:")
    print(f"   Domain: bearstudio.zombie.ads")
    print(f"   Symbol: ETH")
    print(f"   Value: 0.000001 ETH per TX")
    print(f"   Contract: {CONTRACT_ADDRESS}")

    # Ask for number of transactions per wallet
    print(f"\n" + "="*60)
    try:
        tx_per_wallet = int(input("ðŸ“ Berapa TX per wallet? (contoh: 100): ").strip())
        if tx_per_wallet < 1:
            print("âŒ Minimal 1 TX!")
            return
        if tx_per_wallet > 1000:
            print("âš ï¸ Maximum 1000 TX per wallet untuk safety")
            tx_per_wallet = 1000
    except ValueError:
        print("âŒ Input harus angka!")
        return

    # Ask for delay range
    print(f"\nâ±ï¸ Jeda antar transaksi:")
    try:
        delay_min = int(input("   Minimal (detik, default 3): ").strip() or "3")
        delay_max = int(input("   Maksimal (detik, default 10): ").strip() or "10")
        
        if delay_min < 1:
            delay_min = 1
        if delay_max < delay_min:
            delay_max = delay_min + 2
            
    except ValueError:
        delay_min = 3
        delay_max = 10

    # Calculate totals
    total_transactions = len(private_keys) * tx_per_wallet
    estimated_time_min = (total_transactions * delay_min) / 60
    estimated_time_max = (total_transactions * delay_max) / 60
    total_value = total_transactions * 0.000001
    estimated_gas = total_transactions * 0.00005  # Rough estimate

    print(f"\nðŸ“Š Summary:")
    print(f"   Wallets: {len(private_keys)}")
    print(f"   TX per wallet: {tx_per_wallet}")
    print(f"   Total TX: {total_transactions}")
    print(f"   Delay: {delay_min}-{delay_max} seconds")
    print(f"   Total value: ~{total_value:.6f} ETH")
    print(f"   Estimated gas: ~{estimated_gas:.6f} ETH")
    print(f"   Total needed: ~{total_value + estimated_gas:.6f} ETH per wallet")
    print(f"   Estimated time: {estimated_time_min:.1f}-{estimated_time_max:.1f} minutes")

    confirm = input(f"\nâ–¶ï¸  Start? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("âŒ Cancelled")
        return

    # Process each wallet
    total_success = 0
    total_failed = 0
    start_time = time.time()

    for wallet_idx, pk in enumerate(private_keys, 1):
        print(f"\n\n{'#'*60}")
        print(f"# WALLET {wallet_idx}/{len(private_keys)}")
        print(f"{'#'*60}")
        
        wallet_success = 0
        wallet_failed = 0
        
        for tx_idx in range(1, tx_per_wallet + 1):
            tx_number = (wallet_idx - 1) * tx_per_wallet + tx_idx
            
            if send_exact_transaction(pk, tx_number, total_transactions):
                wallet_success += 1
                total_success += 1
            else:
                wallet_failed += 1
                total_failed += 1
            
            # Delay between transactions
            if tx_idx < tx_per_wallet or wallet_idx < len(private_keys):
                delay = random.randint(delay_min, delay_max)
                remaining_tx = total_transactions - tx_number
                
                print(f"\nâ³ Delay {delay}s | Remaining: {remaining_tx} TX", end='')
                
                # Countdown
                for i in range(delay, 0, -1):
                    print(f"\râ³ Delay {delay}s | Remaining: {remaining_tx} TX | Wait: {i}s  ", end='', flush=True)
                    time.sleep(1)
                print()  # New line after countdown
        
        # Wallet summary
        print(f"\n{'='*60}")
        print(f"Wallet {wallet_idx} Summary: âœ… {wallet_success} | âŒ {wallet_failed}")
        print(f"{'='*60}")

    # Final summary
    elapsed = time.time() - start_time
    
    print(f"\n\n{'='*60}")
    print(f"ðŸŽ‰ FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"â±ï¸  Total time: {elapsed/60:.2f} minutes ({elapsed:.0f} seconds)")
    print(f"ðŸ“ Total wallets: {len(private_keys)}")
    print(f"ðŸ“Š Total TX sent: {total_transactions}")
    print(f"âœ… Successful: {total_success}")
    print(f"âŒ Failed: {total_failed}")
    
    if total_transactions > 0:
        success_rate = (total_success / total_transactions) * 100
        print(f"ðŸ“ˆ Success rate: {success_rate:.2f}%")
        
        if total_success > 0:
            avg_time_per_tx = elapsed / total_success
            print(f"âš¡ Average time per TX: {avg_time_per_tx:.2f}s")
    
    print(f"{'='*60}")
    
    if total_success > 0:
        print(f"\nðŸŽ‰ Selamat! {total_success} transaksi berhasil!")
    
    if total_failed > 0:
        print(f"\nâš ï¸ {total_failed} transaksi gagal. Check logs untuk detail.")

if __name__ == "__main__":
    main()
