#!/usr/bin/env fish
if not set --query NS
    echo "Error: requires an NS k8s namespace var." >&2
    exit 1
end

echo "Disk usage for Persistent Volumes"
echo "---------------------------------"
# ! limited to helm-managed pods, consider removing selector
set PODS (kubectl --namespace "$NS" get pods -l app.kubernetes.io/managed-by=Helm -o name | sed "s|pod/||")
# find longest pod name
set PADNUM 0
for POD in $PODS
    set LEN (string length $POD)
    if [ $LEN -gt $PADNUM ]
        set PADNUM $LEN
    end
end
set PADNUM (math $PADNUM + 1)
string pad --char " " --right --width $PADNUM Pod | tr -d "\n"
echo -e "Filesystem      Size  Used Avail Use% Mounted on"
for POD in $PODS
    set PADDED_PODNAME (string pad --char " " --right --width $PADNUM $POD | tr -d "\n")
    kubectl --namespace $NS exec $POD -- df -h 2>/dev/null | grep '^/dev/' | sed "s|^|$PADDED_PODNAME|"
end
