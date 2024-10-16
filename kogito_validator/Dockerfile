FROM maven:3.8-eclipse-temurin-17 AS builder

WORKDIR /app

COPY pom.xml .
COPY src ./src

RUN mvn clean package
RUN find /app/target/

FROM eclipse-temurin:17-jre-jammy

WORKDIR /app

COPY --from=builder /app/target/my-workflow-project-1.0-SNAPSHOT.jar ./app.jar
COPY --from=builder /app/target/dependency/* ./dependency/

ENTRYPOINT java -cp app.jar:dependency/* com.example.DefinitionFileExecutor /workflow.sw.json
