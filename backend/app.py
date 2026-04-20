from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import redis
import os
from datetime import timedelta

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Redis connection
redis_client = redis.from_url(
    os.environ.get('REDIS_URL', 'redis://localhost:6379'),
    decode_responses=True
)

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/counter', methods=['GET'])
def get_counter():
    try:
        count = redis_client.get('visitor_count')
        if count is None:
            count = 0
            redis_client.set('visitor_count', count)
        return jsonify({'success': True, 'count': int(count)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/increment', methods=['POST'])
def increment_counter():
    try:
        new_count = redis_client.incr('visitor_count')
        return jsonify({'success': True, 'count': new_count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_counter():
    try:
        redis_client.set('visitor_count', 0)
        return jsonify({'success': True, 'count': 0})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/store', methods=['POST'])
def store_data():
    try:
        data = request.json
        key = data.get('key')
        value = data.get('value')
        if not key or not value:
            return jsonify({'success': False, 'error': 'key and value required'}), 400
        redis_client.set(key, value)
        return jsonify({'success': True, 'message': 'Data stored successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get/<key>', methods=['GET'])
def get_data(key):
    try:
        value = redis_client.get(key)
        return jsonify({'success': True, 'key': key, 'value': value})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
