FROM nginx:alpine

# Copy the landing page files
COPY index.html /usr/share/nginx/html/
COPY *.png /usr/share/nginx/html/
COPY favicon.ico /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
