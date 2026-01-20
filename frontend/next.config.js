/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable strict mode for better development experience
  reactStrictMode: true,
  
  // Configure API rewrites if needed for production
  async rewrites() {
    return [
      // Proxy API requests to backend in development
      // Uncomment for production if using same domain
      // {
      //   source: '/api/:path*',
      //   destination: 'http://localhost:8000/api/:path*',
      // },
    ];
  },
};

module.exports = nextConfig;
