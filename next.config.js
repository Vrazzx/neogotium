/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",  // ← это генерирует .next/standalone для Docker

  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://backend:8000/api/:path*",
      },
      {
        source: "/webhook",
        destination: "http://backend:8000/webhook",
      },
    ];
  },
};

module.exports = nextConfig;