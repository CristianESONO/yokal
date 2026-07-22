import requests
from decimal import Decimal
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class CurrencyConverter:
    """Convertisseur de devises via ExchangeRate-API"""
    
    # API Configuration
    API_BASE_URL = "https://v6.exchangerate-api.com/v6"
    API_KEY = getattr(settings, 'EXCHANGE_RATE_API_KEY', '')
    CACHE_TIMEOUT = 3600  # Cache 1 heure
    
    # Taux de secours (si API down)
    FALLBACK_RATES = {
        'XOF': 1.0,
        'EUR': 0.00152,
        'USD': 0.00167,
    }
    
    SUPPORTED_CURRENCIES = ['XOF', 'EUR', 'USD']
    
    @staticmethod
    def fetch_rates_from_api(base_currency: str = 'XOF') -> dict:
        """
        Récupérer les taux depuis l'API ExchangeRate
        
        Format: GET https://v6.exchangerate-api.com/v6/YOUR-API-KEY/latest/USD
        """
        # Vérifier le cache d'abord
        cache_key = f"exchange_rates_{base_currency}"
        cached_rates = cache.get(cache_key)
        
        if cached_rates:
            logger.info(f"✅ Taux en cache pour {base_currency}")
            return cached_rates
        
        try:
            # Construire l'URL
            url = f"{CurrencyConverter.API_BASE_URL}/{CurrencyConverter.API_KEY}/latest/{base_currency}"
            
            logger.info(f"🔄 Récupération des taux depuis API pour {base_currency}")
            
            # Faire la requête
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            # Parser la réponse
            data = response.json()
            
            # Vérifier si succès
            if data.get('result') != 'success':
                error_type = data.get('error-type', 'unknown')
                logger.error(f"❌ Erreur API: {error_type}")
                return None
            
            # Formater les données
            rates = {
                'base': data['base_code'],
                'rates': data['conversion_rates'],
                'timestamp': timezone.now().isoformat(),
                'next_update': data.get('time_next_update_utc', 'Unknown')
            }
            
            # Mettre en cache
            cache.set(cache_key, rates, CurrencyConverter.CACHE_TIMEOUT)
            logger.info(f"✅ Taux récupérés et cachés pour {base_currency}")
            
            return rates
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Erreur réseau: {e}. Utilisation des taux de secours.")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération: {e}")
            return None
    
    @staticmethod
    def get_rate(from_currency: str, to_currency: str) -> Decimal:
        """
        Obtenir le taux de change entre deux devises
        
        Exemple: get_rate('XOF', 'EUR') retourne 0.00152
        """
        if from_currency == to_currency:
            return Decimal('1.0')
        
        # Valider les devises
        if from_currency not in CurrencyConverter.SUPPORTED_CURRENCIES:
            logger.warning(f"⚠️ Devise non supportée: {from_currency}")
            return Decimal('1.0')
        
        if to_currency not in CurrencyConverter.SUPPORTED_CURRENCIES:
            logger.warning(f"⚠️ Devise non supportée: {to_currency}")
            return Decimal('1.0')
        
        try:
            # Essayer l'API d'abord
            rates_data = CurrencyConverter.fetch_rates_from_api(from_currency)
            
            if rates_data and to_currency in rates_data['rates']:
                rate = rates_data['rates'][to_currency]
                logger.info(f"✅ Taux obtenu: 1 {from_currency} = {rate} {to_currency}")
                return Decimal(str(rate))
            
            # Fallback si devise manquante
            logger.warning(f"⚠️ Devise {to_currency} non trouvée. Utilisation fallback.")
            from_rate = Decimal(str(CurrencyConverter.FALLBACK_RATES.get(from_currency, 1.0)))
            to_rate = Decimal(str(CurrencyConverter.FALLBACK_RATES.get(to_currency, 1.0)))
            return to_rate / from_rate
            
        except Exception as e:
            logger.error(f"❌ Erreur conversion: {e}")
            # Utiliser les taux de secours
            from_rate = Decimal(str(CurrencyConverter.FALLBACK_RATES.get(from_currency, 1.0)))
            to_rate = Decimal(str(CurrencyConverter.FALLBACK_RATES.get(to_currency, 1.0)))
            return to_rate / from_rate
    
    @staticmethod
    def convert(amount: float, from_currency: str, to_currency: str) -> float:
        """
        Convertir un montant d'une devise à l'autre
        
        Exemple: convert(1000, 'XOF', 'EUR') retourne 1.52
        """
        if from_currency == to_currency:
            return amount
        
        rate = CurrencyConverter.get_rate(from_currency, to_currency)
        result = float(Decimal(str(amount)) * rate)
        
        logger.debug(f"Conversion: {amount} {from_currency} = {result} {to_currency}")
        return result
    
    @staticmethod
    def format_price(amount: float, currency_code: str) -> str:
        """
        Formater le prix avec la devise
        
        Exemple: format_price(10000, 'XOF') retourne "10,000.00 FCFA"
        """
        symbols = {
            'XOF': 'FCFA',
            'EUR': '€',
            'USD': '$',
        }
        
        symbol = symbols.get(currency_code, currency_code)
        
        # Formater avec 2 décimales et séparateurs de milliers
        formatted = f"{amount:,.2f}"
        return f"{formatted} {symbol}"
    
    @staticmethod
    def get_all_prices(amount: float, base_currency: str = 'XOF') -> dict:
        """
        Obtenir le prix dans toutes les devises
        
        Retourne: {'XOF': 10000, 'EUR': 15.2, 'USD': 16.7}
        """
        return {
            'XOF': CurrencyConverter.convert(amount, base_currency, 'XOF'),
            'EUR': CurrencyConverter.convert(amount, base_currency, 'EUR'),
            'USD': CurrencyConverter.convert(amount, base_currency, 'USD'),
        }
    
    @staticmethod
    def get_all_prices_formatted(amount: float, base_currency: str = 'XOF') -> dict:
        """
        Obtenir tous les prix formatés avec devise
        
        Retourne: {'XOF': '10,000.00 FCFA', 'EUR': '15.20 €', 'USD': '16.70 $'}
        """
        prices = CurrencyConverter.get_all_prices(amount, base_currency)
        return {
            currency: CurrencyConverter.format_price(price, currency)
            for currency, price in prices.items()
        }
    
    @staticmethod
    def get_api_status() -> dict:
        """Obtenir le statut de l'API"""
        try:
            url = f"{CurrencyConverter.API_BASE_URL}/{CurrencyConverter.API_KEY}/quota"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data.get('result') == 'success':
                return {
                    'status': 'online',
                    'plan_quota': data['plan_quota'],
                    'requests_remaining': data['requests_remaining'],
                    'refresh_day': data['refresh_day_of_month']
                }
            else:
                return {'status': 'error', 'error': data.get('error-type')}
        except Exception as e:
            return {'status': 'offline', 'error': str(e)}