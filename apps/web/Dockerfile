FROM node:20-alpine AS deps
WORKDIR /repo
COPY package.json package-lock.json ./
COPY apps/web/package.json ./apps/web/package.json
COPY packages/shared_types/package.json ./packages/shared_types/package.json
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /repo
# NEXT_PUBLIC_* variables are inlined at build time, not runtime.
# Pass the public API URL as a build argument so it is baked into the bundle.
# docker build --build-arg NEXT_PUBLIC_API_URL=http://your-host:8000 ...
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /repo/node_modules ./node_modules
COPY . .
RUN npm run build --workspace web

FROM node:20-alpine AS runner
WORKDIR /repo/apps/web
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1
COPY --from=builder /repo/node_modules /repo/node_modules
COPY --from=builder /repo/apps/web/package.json ./package.json
COPY --from=builder /repo/apps/web/.next ./.next
COPY --from=builder /repo/apps/web/public ./public
EXPOSE 3000
CMD ["npm", "run", "start"]
