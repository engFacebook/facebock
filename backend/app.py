from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import redis
import os
import logging
from datetime import timedelta

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# إعداد الاتصال بـ Redis
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
logger.info(f"Connecting to Redis at: {redis_url}")

try:
    redis_client = redis.from_url(
        redis_url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )
    # اختبار الاتصال
    redis_client.ping()
    logger.info("✅ Successfully connected to Redis")
except Exception as e:
    logger.error(f"❌ Failed to connect to Redis: {e}")
    redis_client = None

@app.route('/')
def serve_frontend():
    """Serve the main HTML page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/counter', methods=['GET'])
def get_counter():
    """Get current visitor count"""
    try:
        if redis_client is None:
            return jsonify({'success': False, 'error': 'Redis not connected'}), 500
        
        count = redis_client.get('visitor_count')
        if count is None:
            count = 0
            redis_client.set('visitor_count', count)
        
        return jsonify({'success': True, 'count': int(count)})
    except Exception as e:
        logger.error(f"Error in get_counter: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/increment', methods=['POST'])
def increment_counter():
    """Increment visitor count"""
    try:
        if redis_client is None:
            return jsonify({'success': False, 'error': 'Redis not connected'}), 500
        
        new_count = redis_client.incr('visitor_count')
        logger.info(f"Counter incremented to: {new_count}")
        return jsonify({'success': True, 'count': new_count})
    except Exception as e:
        logger.error(f"Error in increment_counter: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_counter():
    """Reset visitor count to zero"""
    try:
        if redis_client is None:
            return jsonify({'success': False, 'error': 'Redis not connected'}), 500
        
        redis_client.set('visitor_count', 0)
        logger.info("Counter reset to 0")
        return jsonify({'success': True, 'count': 0})
    except Exception as e:
        logger.error(f"Error in reset_counter: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/store', methods=['POST'])
def store_data():
    """Store custom data in Redis"""
    try:
        if redis_client is None:
            return jsonify({'success': False, 'error': 'Redis not connected'}), 500
        
        data = request.json
        key = data.get('key')
        value = data.get('value')
        
        if not key or not value:
            return jsonify({'success': False, 'error': 'key and value are required'}), 400
        
        redis_client.set(key, value)
        logger.info(f"Data stored - Key: {key}, Value: {value}")
        return jsonify({'success': True, 'message': f'Data stored successfully under key: {key}'})
    except Exception as e:
        logger.error(f"Error in store_data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get/<key>', methods=['GET'])
def get_data(key):
    """Retrieve data from Redis by key"""
    try:
        if redis_client is None:
            return jsonify({'success': False, 'error': 'Redis not connected'}), 500
        
        value = redis_client.get(key)
        if value is None:
            return jsonify({'success': False, 'error': f'No data found for key: {key}'}), 404
        
        logger.info(f"Data retrieved - Key: {key}, Value: {value}")
        return jsonify({'success': True, 'key': key, 'value': value})
    except Exception as e:
        logger.error(f"Error in get_data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete/<key>', methods=['DELETE'])
def delete_data(key):
    """Delete data from Redis by key"""
    try:
        if redis_client is None:
            return jsonify({'success': False, 'error': 'Redis not connected'}), 500
        
        deleted = redis_client.delete(key)
        if deleted:
            logger.info(f"Data deleted - Key: {key}")
            return jsonify({'success': True, 'message': f'Key {key} deleted successfully'})
        else:
            return jsonify({'success': False, 'error': f'Key {key} not found'}), 404
    except Exception as e:
        logger.error(f"Error in delete_data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/keys', methods=['GET'])
def get_all_keys():
    """Get all keys in Redis (for debugging)"""
    try:
        if redis_client is None:
            return jsonify({'success': False, 'error': 'Redis not connected'}), 500
        
        keys = redis_client.keys('*')
        return jsonify({'success': True, 'keys': keys})
    except Exception as e:
        logger.error(f"Error in get_all_keys: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Health check endpoint for Railway
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'redis_connected': redis_client is not None}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
