# Use OpenJDK 17 as the base image
FROM openjdk:17-jdk-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the JAR file from the target directory
COPY target/*.jar app.jar

# Expose the port the app runs on
EXPOSE 8081

# Run the JAR file
ENTRYPOINT ["java", "-jar", "app.jar"]