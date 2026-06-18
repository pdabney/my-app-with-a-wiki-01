# Primary store for short links. In real Terraform, prefer provider default_tags
# so the required set is applied once; this sample keeps tags on the resource.

resource "aws_dynamodb_table" "links" {
  # @intent authoritative store of short code -> destination URL; on-demand billing.
  name         = "linkshort-links"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "code"

  attribute {
    name = "code"
    type = "S"
  }

  tags = {
    Owner       = "platform-team"
    Environment = "prod"
    CostCenter  = "cc-5678"
    Service     = "linkshort"
  }
}
