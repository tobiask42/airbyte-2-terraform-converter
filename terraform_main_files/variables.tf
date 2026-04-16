variable "server_url" {
    description = "The airbyte API URL (target)"
    type = string
  
}

variable "client_id" {
    description = "The Airbyte Client ID"
    type = string
}

variable "client_secret" {
    description = "The Airbyte Client Secret"
    type = string
    sensitive = true
}

variable "workspace_id" {
    description = "ID of the Airbyte Workspace"
    type = string
}

variable "workspace_name" {
    description = "Name of the Airbyte Workspace"
    type = string
}

variable "username" {
    description = "Username of the Airbyte User"
    type = string
}

variable "password" {
    description = "Password of the Airbyte User"
    type = string
  
}