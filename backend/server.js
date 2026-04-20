const express = require('express');
const redis = require('redis');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// إعداد الاتصال بـ Redis
const redisClient = redis.createClient({
    url: process.env.REDIS_URL || 'redis://localhost:6379'
});

redisClient.on('error', (err) => console.error('Redis Error:', err));
redisClient.on('connect', () => console.log('✅ Connected to Redis'));

// الاتصال بـ Redis
(async () => {
    await redisClient.connect();
})();

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend')));

// API: جلب العداد الحالي
app.get('/api/counter', async (req, res) => {
    try {
        let count = await redisClient.get('visitor_count');
        if (count === null) {
            count = 0;
            await redisClient.set('visitor_count', count);
        }
        res.json({ success: true, count: parseInt(count) });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// API: زيادة العداد
app.post('/api/increment', async (req, res) => {
    try {
        const newCount = await redisClient.incr('visitor_count');
        res.json({ success: true, count: newCount });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// API: إعادة تعيين العداد
app.post('/api/reset', async (req, res) => {
    try {
        await redisClient.set('visitor_count', 0);
        res.json({ success: true, count: 0 });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// API: تخزين بيانات جديدة
app.post('/api/store', async (req, res) => {
    try {
        const { key, value } = req.body;
        if (!key || !value) {
            return res.status(400).json({ success: false, error: 'key and value required' });
        }
        await redisClient.set(key, value);
        res.json({ success: true, message: 'Data stored successfully' });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// API: استرجاع بيانات
app.get('/api/get/:key', async (req, res) => {
    try {
        const value = await redisClient.get(req.params.key);
        res.json({ success: true, key: req.params.key, value: value });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

app.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
});
