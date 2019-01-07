#!/bin/bash
#execute locust test with specified duration and hatch rate
locust -f deezer_performance.py &
LOCUST_PID=$!
echo $LOCUST_PID
sleep 2
curl --data "hatch_rate=5&locust_count=5" http://localhost:8089/swarm #
sleep 300     # execution time
curl localhost:8089/stats/requests/csv -o requests_stats1.csv
curl localhost:8089/stats/distribution/csv -o response_stats1.csv
kill -9 $LOCUST_PID
locust -f deezer_performance.py &
LOCUST_PID=$!
echo $LOCUST_PID
sleep 2
curl --data "hatch_rate=10&locust_count=10" http://localhost:8089/swarm #
sleep 300    # execution time
curl localhost:8089/stats/requests/csv -o requests_stats2.csv
curl localhost:8089/stats/distribution/csv -o response_stats2.csv
kill -9 $LOCUST_PID
locust -f deezer_performance.py &
LOCUST_PID=$!
echo $LOCUST_PID
sleep 2
curl --data "hatch_rate=20&locust_count=20" http://localhost:8089/swarm #
sleep 300    # execution time
curl localhost:8089/stats/requests/csv -o requests_stats3.csv
curl localhost:8089/stats/distribution/csv -o response_stats3.csv
kill -9 $LOCUST_PID
