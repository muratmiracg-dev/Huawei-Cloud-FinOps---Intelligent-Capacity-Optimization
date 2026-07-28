{{- define "finops-optimizer.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "finops-optimizer.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name (include "finops-optimizer.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{- define "finops-optimizer.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "finops-optimizer.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: huawei-finops
{{- end }}

{{- define "finops-optimizer.selectorLabels" -}}
app.kubernetes.io/name: {{ include "finops-optimizer.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "finops-optimizer.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "finops-optimizer.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
