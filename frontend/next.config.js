/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '9000',
        pathname: '/chatflow-files/**',
      },
      {
        protocol: 'http',
        hostname: 'minio',
        port: '9000',
        pathname: '/chatflow-files/**',
      },
    ],
  },
}

module.exports = nextConfig
