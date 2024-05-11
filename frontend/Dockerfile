FROM node:18-alpine

WORKDIR /frontend/web

ENV TZ Asia/Tokyo
COPY --chown=node:node web/package*.json ./


RUN yarn install

COPY ./web ./

# Expose the port the app runs on
EXPOSE 3000


# run the React app
CMD  ["yarn", "dev"]
