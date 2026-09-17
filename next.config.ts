import type { NextConfig } from "next";

/**
 * In development the pages and the Python endpoint are two processes, so `/api` is
 * proxied to the one `make api` starts. On Vercel the function is part of the same
 * deployment and this rewrite does not exist.
 */
const DEVELOPMENT_API = "http://127.0.0.1:5328/api/:path*";

const nextConfig: NextConfig = {
  async rewrites() {
    if (process.env.NODE_ENV !== "development") {
      return [];
    }
    return [{ source: "/api/:path*", destination: DEVELOPMENT_API }];
  },

  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-Robots-Tag", value: "noindex, nofollow" },
          { key: "Referrer-Policy", value: "no-referrer" },
        ],
      },
    ];
  },
};

export default nextConfig;
