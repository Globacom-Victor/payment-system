import click
from payment_service_v2 import PaymentServiceV2
from database import get_session
from sqlalchemy.exc import SQLAlchemyError
from crypto_api import CryptoAPIException
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """🚀 Cryptocurrency Payment System CLI
    
    Real-time exchange rates powered by CoinGecko
    Wallet validation via Blockchain.com & Etherscan
    """
    pass

@cli.command()
@click.option('--crypto', required=True, help='Cryptocurrency (BTC, ETH, LTC, XRP)')
@click.option('--fiat', required=True, help='Fiat currency (USD, EUR, GBP, JPY, CAD, AUD)')
@click.option('--amount', required=True, type=float, help='Amount in fiat currency')
@click.option('--wallet', required=True, help='Destination wallet address')
def purchase(crypto, fiat, amount, wallet):
    """💳 Create a cryptocurrency purchase
    
    Example:
        python cli_v2.py purchase --crypto BTC --fiat USD --amount 100 --wallet bc1q09nu70j26mgln6x9tha6eerlv80d6uzn588u0v
    """
    session = None
    try:
        session = get_session()
        payment_service = PaymentServiceV2(session)
        
        click.echo(click.style('\n⏳ Processing purchase...\n', fg='cyan'))
        
        transaction = payment_service.create_purchase(
            crypto_symbol=crypto.upper(),
            fiat_symbol=fiat.upper(),
            fiat_amount=amount,
            wallet_address=wallet
        )
        
        click.echo(click.style('✅ Purchase created successfully!\n', fg='green', bold=True))
        click.echo(click.style('Transaction Details:', bold=True))
        click.echo(f'  Transaction ID: {transaction.id}')
        click.echo(f'  Status: {transaction.status}')
        click.echo(f'  Exchange Rate: 1 {transaction.crypto_symbol} = {transaction.exchange_rate} {transaction.fiat_symbol}')
        click.echo(f'  Fiat Amount: {transaction.fiat_amount} {transaction.fiat_symbol}')
        click.echo(f'  Crypto Amount: {transaction.crypto_amount} {transaction.crypto_symbol}')
        click.echo(f'  Wallet: {transaction.wallet_address}')
        click.echo(f'  Created: {transaction.created_at}')
        click.echo()
        
    except ValueError as e:
        click.echo(click.style(f'❌ Validation Error: {str(e)}', fg='red'), err=True)
        logger.error(f"Validation error: {str(e)}")
        raise click.Exit(1)
    except CryptoAPIException as e:
        click.echo(click.style(f'❌ API Error: {str(e)}', fg='red'), err=True)
        logger.error(f"API error: {str(e)}")
        raise click.Exit(1)
    except SQLAlchemyError as e:
        click.echo(click.style(f'❌ Database Error: {str(e)}', fg='red'), err=True)
        logger.error(f"Database error: {str(e)}")
        raise click.Exit(1)
    except Exception as e:
        click.echo(click.style(f'❌ Unexpected Error: {str(e)}', fg='red'), err=True)
        logger.error(f"Unexpected error: {str(e)}")
        raise click.Exit(1)
    finally:
        if session:
            session.close()

@cli.command()
@click.option('--crypto', required=True, help='Cryptocurrency (BTC, ETH, LTC, XRP)')
@click.option('--fiat', required=True, help='Fiat currency')
def market(crypto, fiat):
    """📊 Get real-time market data
    
    Example:
        python cli_v2.py market --crypto BTC --fiat USD
    """
    session = None
    try:
        session = get_session()
        payment_service = PaymentServiceV2(session)
        
        click.echo(click.style(f'\n📈 Market Data for {crypto.upper()}/{fiat.upper()}\n', fg='cyan'))
        
        market_data = payment_service.get_market_data(crypto, fiat)
        
        click.echo(f"  Price: {market_data['price']} {fiat.upper()}")
        if market_data['market_cap']:
            click.echo(f"  Market Cap: ${market_data['market_cap']:,.0f} {fiat.upper()}")
        if market_data['volume_24h']:
            click.echo(f"  24h Volume: ${market_data['volume_24h']:,.0f} {fiat.upper()}")
        if market_data['change_24h']:
            change_color = 'green' if market_data['change_24h'] > 0 else 'red'
            change_symbol = '📈' if market_data['change_24h'] > 0 else '📉'
            click.echo(click.style(f"  24h Change: {change_symbol} {market_data['change_24h']:.2f}%", fg=change_color))
        click.echo()
        
    except CryptoAPIException as e:
        click.echo(click.style(f'❌ API Error: {str(e)}', fg='red'), err=True)
        raise click.Exit(1)
    finally:
        if session:
            session.close()

@cli.command()
@click.option('--transaction-id', required=True, help='Transaction ID')
def status(transaction_id):
    """📋 Check transaction status
    
    Example:
        python cli_v2.py status --transaction-id a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6
    """
    session = None
    try:
        session = get_session()
        payment_service = PaymentServiceV2(session)
        
        transaction = payment_service.get_transaction_status(transaction_id)
        
        status_colors = {
            'pending': 'yellow',
            'confirmed': 'blue',
            'completed': 'green',
            'failed': 'red',
        }
        status_icons = {
            'pending': '⏳',
            'confirmed': '✓',
            'completed': '✅',
            'failed': '❌',
        }
        
        click.echo()
        click.echo(click.style('Transaction Status:', bold=True))
        click.echo(f'  ID: {transaction.id}')
        click.echo(click.style(f'  Status: {status_icons.get(transaction.status, "?")} {transaction.status.upper()}',
                              fg=status_colors.get(transaction.status, 'white')))
        click.echo(f'  Crypto: {transaction.crypto_amount} {transaction.crypto_symbol}')
        click.echo(f'  Fiat: {transaction.fiat_amount} {transaction.fiat_symbol}')
        click.echo(f'  Wallet: {transaction.wallet_address}')
        click.echo(f'  Created: {transaction.created_at}')
        click.echo(f'  Updated: {transaction.updated_at}')
        click.echo()
        
    except ValueError as e:
        click.echo(click.style(f'❌ Error: {str(e)}', fg='red'), err=True)
        raise click.Exit(1)
    finally:
        if session:
            session.close()

@cli.command(name='list')
def list_transactions():
    """📋 List all transactions
    
    Example:
        python cli_v2.py list
    """
    session = None
    try:
        session = get_session()
        payment_service = PaymentServiceV2(session)
        
        transactions = payment_service.get_all_transactions()
        
        if not transactions:
            click.echo(click.style('No transactions found.', fg='yellow'))
            return
        
        click.echo(click.style(f'\n💰 Transactions ({len(transactions)} total)\n', fg='cyan'))
        click.echo('=' * 100)
        
        for tx in transactions:
            status_colors = {
                'pending': 'yellow',
                'confirmed': 'blue',
                'completed': 'green',
                'failed': 'red',
            }
            status_icon = '⏳' if tx.status == 'pending' else '✓'
            
            click.echo(f'ID: {tx.id}')
            click.echo(click.style(f'Status: {status_icon} {tx.status.upper()}', fg=status_colors.get(tx.status, 'white')))
            click.echo(f'Transaction: {tx.fiat_amount} {tx.fiat_symbol} → {tx.crypto_amount} {tx.crypto_symbol}')
            click.echo(f'Wallet: {tx.wallet_address}')
            click.echo(f'Rate: 1 {tx.crypto_symbol} = {tx.exchange_rate} {tx.fiat_symbol}')
            click.echo(f'Created: {tx.created_at}')
            click.echo('-' * 100)
        
    except Exception as e:
        click.echo(click.style(f'❌ Error: {str(e)}', fg='red'), err=True)
        raise click.Exit(1)
    finally:
        if session:
            session.close()

if __name__ == '__main__':
    cli()
