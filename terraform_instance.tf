
provider "google" {
  version = "3.5.0"

  credentials = file("new-key.json")

  project = "deployment-manager-test-282406"
  region  = "us-central1"
  zone    = "us-central1-c"
}

resource "google_compute_instance" "appserver" {
  name = "secondary-application-server"
  machine_type = "f1-micro"

  boot_disk {
   initialize_params {
     image = "debian-cloud/debian-9"
   }
}
 network_interface {
   network = "default"
}
}