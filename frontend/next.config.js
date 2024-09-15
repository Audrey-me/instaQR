// next.config.js
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/proxy',
        destination: 'http://backend-service:8000/generate-qr/',
      },
    ];
  },
};

