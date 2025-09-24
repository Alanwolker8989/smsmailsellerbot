import redis

# Укажи ID админов
TG_ADMIN_IDS = [7235203514]  # Замени на свои ID

# Подключение к Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)