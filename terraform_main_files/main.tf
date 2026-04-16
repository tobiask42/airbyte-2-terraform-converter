terraform {
  required_providers {
    airbyte = {
      source = "airbytehq/airbyte"
      version = "1.0.0-rc6"
    }
  }
}

provider "airbyte" {
    server_url = var.server_url
    #client_id = var.client_id
    #client_secret = var.client_secret
    username = var.username
    password = var.password
}