import type { MetadataRoute } from "next";

/**
 * Disallows everything. The access token is deliberately absent: a disallow rule
 * naming the protected path would publish the thing it protects.
 */
export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", disallow: "/" },
  };
}
