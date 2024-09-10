FROM node:18-alpine

# set the working directory in the container
WORKDIR /app

# copy over the package.json content and package-lock.json file to the container
COPY package*.json ./

# install dependencies
RUN npm install

# copy the rest of the application over to the container
COPY . .

# build the application
RUN npm run build

# expose the port on which the app runs 
EXPOSE 3000

# start the application
CMD ["npm", "start"]
