FROM eclipse-temurin:17-jdk-alpine as builder
WORKDIR /app
COPY pom.xml .
COPY travel-plan-service/pom.xml travel-plan-service/pom.xml
COPY common/pom.xml common/pom.xml
RUN mvn dependency:go-offline -B
COPY travel-plan-service/src travel-plan-service/src
COPY common/src common/src
RUN mvn package -DskipTests -B

FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# 设置时区
ENV TZ=Asia/Shanghai

# 创建非 root 用户运行
RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring

# 复制 jar 文件
COPY --from=builder /app/travel-assistant/travel-plan-service/target/*.jar app.jar

# 暴露端口
EXPOSE 8083

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8083/health || exit 1

# 启动应用
ENTRYPOINT ["java", "-jar", "app.jar"]
