import redis
from flask import current_app
from collections import defaultdict
import json

class RedisCache:
    def __init__(self, redis_url=None, ttl=3600):
        self.redis_client = None
        self.ttl = ttl
        if redis_url:
            try:
                self.redis_client = redis.StrictRedis.from_url(redis_url, decode_responses=False)
                # Тестируем соединение
                self.redis_client.ping()
            except Exception as e:
                self.redis_client = None  # decode_responses=True для строк
    
    def init_app(self, app):
        redis_url = app.config.get('REDIS_URL')
        self.ttl = app.config.get('REDIS_CACHE_TTL', 3600)
        if redis_url:
            try:
                self.redis_client = redis.StrictRedis.from_url(redis_url, decode_responses=False)
                # Тестируем соединение
                self.redis_client.ping()
                app.logger.info("Redis подключен успешно init_app")
                app.logger.info(f"self.redis_client: {self.redis_client}")
            except Exception as e:
                app.logger.error(f"Ошибка подключения к Redis init_app: {e}")
                self.redis_client = None
        app.extensions['redis_cache'] = self

    def set_cache(self, key, value, ttl=None):
        if not self.redis_client:
            return False
        try:
            ttl = ttl or self.ttl
            # Используем JSON для сериализации
            serialized = json.dumps(value, ensure_ascii=False)
            return self.redis_client.setex(key, ttl, serialized)
        except Exception as e:
            current_app.logger.error(f"Redis set error for key {key}: {e}")
            return False
    
    def get_cache(self, key, default=None):
        if not self.redis_client:
            return default
        try:
            data = self.redis_client.get(key)
            current_app.logger.debug(f"Полученны данные по ключу {key}: {data} {json.loads(data)}")
            if data:
                return json.loads(data)
            return default
        except Exception as e:
            current_app.logger.error(f"Redis get error for key {key}: {e}")
            return default
    
    def delete_cache(self, key):
        if not self.redis_client:
            return False
        try:
            return self.redis_client.delete(key)
        except Exception as e:
            current_app.logger.error(f"Redis delete error for key {key}: {e}")
            return False
    
    def exists(self, key):
        if not self.redis_client:
            return False
        try:
            return self.redis_client.exists(key)
        except Exception as e:
            current_app.logger.error(f"Redis exists error for key {key}: {e}")
            return False

# Создаем глобальный экземпляр
# redis_cache = RedisCache()

# ===== ФУНКЦИИ ДЛЯ КЭШИРОВАНИЯ ТРЕХ КЛЮЧЕЙ =====

def build_and_cache_questions_by_pool(redis_cache, returnonlypool=False):
    """Строит и кэширует словарь вопросов по пулам"""
    current_app.logger.debug("========== build_and_cache_questions_by_pool ==========")
    from .models import Question
    try:
        pool_map = defaultdict(list)
        questions = Question.query.with_entities(Question.id, Question.pool).all()
        for q_id, pool in questions:
            if pool:
                pool_map[pool].append(q_id)
        
        result = dict(pool_map)
        redis_cache.set_cache('QUESTIONS_BY_POOL', result)
        redis_cache.set_cache('POOL_SIZE', len(result))
        if returnonlypool:
            return len(result)
        else:
            return result
    except Exception as e:
        current_app.logger.error(f"Error building questions by pool: {e}")
        return {} 

def build_and_cache_correct_answers(redis_cache):
    current_app.logger.debug("========== build_and_cache_correct_answers ==========")
    """Строит и кэширует словарь правильных ответов"""
    from .models import Option
    try:
        correct_answers = defaultdict(list)
        for opt in Option.query.filter_by(is_correct=True).all():
            correct_answers[opt.question_id].append(opt.plain_values.lower().strip())
        
        result = dict(correct_answers)
        redis_cache.set_cache('CORRECT_ANSWERS', result)
        current_app.logger.info(f"CORRECT_ANSWERS cached: {len(result)} questions")
        return result
    except Exception as e:
        current_app.logger.error(f"Error building correct answers: {e}")
        return {}

# ===== ФУНКЦИИ ДЛЯ ПОЛУЧЕНИЯ ИЗ КЭША =====

def get_questions_by_pool(redis_cache):
    """Получает словарь вопросов по пулам из кэша или строит заново"""
    current_app.logger.debug("========== get_questions_by_pool ==========")
    result = redis_cache.get_cache('QUESTIONS_BY_POOL')
    if result is None:
        result = build_and_cache_questions_by_pool()
    return result

def get_correct_answers(redis_cache):
    """Получает словарь правильных ответов из кэша или строит заново"""
    current_app.logger.debug("========== get_correct_answers ==========")
    result = redis_cache.get_cache('CORRECT_ANSWERS')
    if result is None:
        result = build_and_cache_correct_answers()
    return result

def get_pool_size(redis_cache):
    """Получает размеры пулов из кэша или строит заново"""
    current_app.logger.debug("========== get_pool_size ==========")
    result = redis_cache.get_cache('POOL_SIZE')
    if result is None:
        result = build_and_cache_questions_by_poolredis_cache(redis_cache, returnonlypool=True)
    return result

# ===== ФУНКЦИИ ДЛЯ ОБНОВЛЕНИЯ КЭША =====

def refresh_all_cache(redis_cache):
    """Обновляет весь кэш (все три ключа)"""
    current_app.logger.debug("========== refresh_all_cache ==========")
    try:
        build_and_cache_questions_by_pool(redis_cache)
        build_and_cache_correct_answers(redis_cache)
        current_app.logger.info("All cache refreshed successfully")
        return True
    except Exception as e:
        current_app.logger.error(f"Error refreshing cache: {e}")
        return False

def refresh_cache_key(redis_cache, key):
    """Обновляет конкретный ключ кэша"""
    current_app.logger.debug("========== refresh_cache_key ==========")
    try:
        if key == 'QUESTIONS_BY_POOL' or key == 'POOL_SIZE':
            return build_and_cache_questions_by_pool()
        elif key == 'CORRECT_ANSWERS':
            return build_and_cache_correct_answers()
        else:
            current_app.logger.warning(f"Unknown cache key: {key}")
            return None
    except Exception as e:
        current_app.logger.error(f"Error refreshing cache key {key}: {e}")
        return None

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

def get_all_cache_status(redis_cache):
    """Возвращает статус всех ключей кэша"""
    current_app.logger.debug("========== get_all_cache_status ==========")
    return {
        'QUESTIONS_BY_POOL': redis_cache.exists('QUESTIONS_BY_POOL'),
        'CORRECT_ANSWERS': redis_cache.exists('CORRECT_ANSWERS'),
        'POOL_SIZE': redis_cache.exists('POOL_SIZE')
    }

def clear_all_cache(redis_cache):
    """Очищает весь кэш"""
    current_app.logger.debug("========== clear_all_cache ==========")
    try:
        redis_cache.delete_cache('QUESTIONS_BY_POOL')
        redis_cache.delete_cache('CORRECT_ANSWERS')
        redis_cache.delete_cache('POOL_SIZE')
        current_app.logger.info("All cache cleared")
        return True
    except Exception as e:
        current_app.logger.error(f"Error clearing cache: {e}")
        return False
