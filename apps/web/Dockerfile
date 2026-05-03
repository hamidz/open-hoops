FROM node:20-alpine AS deps
WORKDIR /repo
COPY package.json package-lock.json ./
COPY apps/web/package.json ./apps/web/package.json
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /repo
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /repo/node_modules ./node_modules
COPY --from=deps /repo/apps/web/node_modules ./apps/web/node_modules
COPY . .
RUN npm run build --workspace web

FROM node:20-alpine AS runner
WORKDIR /repo/apps/web
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1
COPY --from=builder /repo/node_modules /repo/node_modules
COPY --from=builder /repo/apps/web/node_modules ./node_modules
COPY --from=builder /repo/apps/web/package.json ./package.json
COPY --from=builder /repo/apps/web/.next ./.next
COPY --from=builder /repo/apps/web/public ./public
EXPOSE 3000
CMD ["npm", "run", "start"]
