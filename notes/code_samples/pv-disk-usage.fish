#!/usr/bin/env fish
if not set --query NS
    echo "Error: requires an NS k8s namespace var." >&2
    exit 1
end

echo "Disk usage for Persistent Volumes"
echo ----------------------------------
set PODS (kubectl --namespace "$NS" get pods -l app.kubernetes.io/instance=invenio -o name | sed "s|pod/||")
# "invenio-opensearch-coordinating-0" is longest pod name at 33 chars
string pad --char " " --right --width 34 Pod | tr -d "\n"
echo -e "Filesystem      Size  Used Avail Use% Mounted on"
for POD in $PODS
    set PADDED_PODNAME (string pad --char " " --right --width 34 $POD | tr -d "\n")
    kubectl --namespace $NS exec $POD -- df -h 2>/dev/null | grep '^/dev/' | sed "s|^|$PADDED_PODNAME|"
end
