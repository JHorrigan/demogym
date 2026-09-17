import { NextResponse, type NextRequest } from "next/server";

/**
 * Checks the access token in the first path segment against the environment.
 *
 * Every page is covered here rather than each one remembering to check. The Python
 * endpoints repeat the check independently, because they are reachable at their own
 * paths and a check only one deployable performs is not a check. See 0006.
 */
export function proxy(request: NextRequest) {
  const expected = process.env.DEMOGYM_ACCESS_TOKEN;
  if (!expected) {
    throw new Error("DEMOGYM_ACCESS_TOKEN is not set, so no request can be admitted");
  }

  const [, firstSegment] = request.nextUrl.pathname.split("/");
  if (firstSegment === expected) {
    return NextResponse.next();
  }

  return NextResponse.rewrite(new URL("/refused", request.url), { status: 401 });
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|robots.txt).*)"],
};
