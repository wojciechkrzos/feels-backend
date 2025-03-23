workspace "Feels" "Architecture of the Emotion Logging and Sharing application" {

    !identifiers hierarchical

    model {
        user = person "User" "An individual using the application to log and share emotions."
        emotionService = softwareSystem "Feels" "Allows users to log their emotions and share them with friends." {
            mobileApp = container "Mobile Application" "Provides the user interface for logging and sharing emotions." "Kotlin" "Android App"
            backend = container "Backend Service" "Handles business logic and processes client requests." "Django" "REST API"
            database = container "Graph Database" "Stores user emotions and social network data." "Neo4j" "Database"
        }

        user -> emotionService.mobileApp "Uses"
        emotionService.mobileApp -> emotionService.backend "Sends requests to" "HTTPS/JSON"
        emotionService.backend -> emotionService.database "Reads from and writes to" "Bolt protocol"
    }

    views {
        systemContext emotionService "SystemContext" {
            include *
            autolayout lr
        }

        container emotionService "ContainerView" {
            include *
            autolayout lr
        }

        styles {
            element "Person" {
                background #08427b
                color #ffffff
                shape person
            }
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "Database" {
                shape cylinder
            }
        }
    }
}
