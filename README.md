# Minotaur

An automated scanning tool using Dockers & RabbitMQ to help with bug bounties

The whole setup is based on workflows:

1. Passive Subdomains Enumeration -> Dedup & keep new ones -> shuffleDNS -> httprobe -> dirsearch
2. IP or Subnet -> Masscan -> Nmap Services -> Dirsearch http/https ports

## Tools

- RabbitMQ
- Amass / Assetfinder / Findomain / Subfinder / Chaos
- Massdns / Nmap
- Dnsgen
- httprobe / anew
- Dirsearch

## To Do

- [x] Add Dirsearch implementation
- [x] Add Rapid7 Sonar via Crobat
- [ ] Pull fresh Resolvers (via cronjob)
- [x] Scan IP found from Massdns step for Open Ports (masscan / nmap)
- [x] Add shuffleDNS & dnsvalidator tools to wrap arround Massdns
- [ ] Add waybackmachine/commoncrawl results
- [ ] Change dirsearch to ffuf, better html output

## Environment Variables

- You will need a key to run chaos project, create an env file in the root path and add a line with your key

```
CHAOS_KEY=key
```

## Instructions

1. git clone the repo
2. Put resolvers.txt in the docker/input/ directory, which you can get through a daily run of dnsvalidator
3. Put wordlist.txt in the docker/input/ directory, which is the list dirsearch will use
4. Results are stored in docker/output/ directory

- Build using `--compatibility` mode due to the use of replicas for dirsearch.

```
docker-compose --compatibility up --build
```

- At the moment you can run this using:

```
python app/send.py passive domain.com
python app/send.py ip-scan x.x.x.x/x <date>
```

### Extra

- Dirsearch runs with 55555licas, you can edit to add more or less.

### Rabbitmq

Useful commands

Use `docker-compose exec rabbitmq bash` to get into the rabbitmq container

Use `rabbitmqctl list_queues` to get a list of all the queues and the number of messages they have

Use `rabbitmqadmin get queue=dir-scan count=100` to list the last 100 entries in the dir-scan queue
