{{/* ============================================================================
ResilienceAI - Helm Helper Templates
============================================================================ */}}

{{/* Expand the name of the chart */}}
{{- define "resilience-ai.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* Create a default fully qualified app name */}}
{{- define "resilience-ai.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/* Create chart name and version */}}
{{- define "resilience-ai.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* Common labels */}}
{{- define "resilience-ai.labels" -}}
helm.sh/chart: {{ include "resilience-ai.chart" . }}
{{ include "resilience-ai.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/* Selector labels */}}
{{- define "resilience-ai.selectorLabels" -}}
app.kubernetes.io/name: {{ include "resilience-ai.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/* Create the name of the service account */}}
{{- define "resilience-ai.serviceAccountName" -}}
{{- if .Values.app.serviceAccount.create }}
{{- default (include "resilience-ai.fullname" .) .Values.app.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.app.serviceAccount.name }}
{{- end }}
{{- end }}

{{/* Database connection string */}}
{{- define "resilience-ai.databaseUrl" -}}
{{- printf "postgresql://%s:$(DB_PASSWORD)@%s-postgresql:5432/%s" 
    .Values.database.postgresql.auth.username
    (include "resilience-ai.fullname" .)
    .Values.database.postgresql.auth.database }}
{{- end }}

{{/* Redis connection string */}}
{{- define "resilience-ai.redisUrl" -}}
{{- printf "redis://:$(REDIS_PASSWORD)@%s-redis-master:6379/0" 
    (include "resilience-ai.fullname" .) }}
{{- end }}

{{/* Image pull secrets */}}
{{- define "resilience-ai.imagePullSecrets" -}}
{{- if .Values.global.imagePullSecrets }}
imagePullSecrets:
{{- range .Values.global.imagePullSecrets }}
  - name: {{ .name }}
{{- end }}
{{- end }}
{{- end }}

{{/* Node selector */}}
{{- define "resilience-ai.nodeSelector" -}}
{{- if .Values.global.nodeSelector }}
nodeSelector:
{{- toYaml .Values.global.nodeSelector | nindent 2 }}
{{- end }}
{{- end }}

{{/* Tolerations */}}
{{- define "resilience-ai.tolerations" -}}
{{- if .Values.global.tolerations }}
tolerations:
{{- toYaml .Values.global.tolerations | nindent 2 }}
{{- end }}
{{- end }}

{{/* Affinity */}}
{{- define "resilience-ai.affinity" -}}
{{- if .Values.global.affinity }}
affinity:
{{- toYaml .Values.global.affinity | nindent 2 }}
{{- end }}
{{- end }}

{{/* Environment variables from config */}}
{{- define "resilience-ai.env" -}}
{{- range $key, $value := .Values.app.env }}
- name: {{ $key }}
  value: {{ $value | quote }}
{{- end }}
{{- end }}

{{/* Pod annotations */}}
{{- define "resilience-ai.podAnnotations" -}}
{{- if .Values.app.podAnnotations }}
{{- toYaml .Values.app.podAnnotations }}
{{- end }}
prometheus.io/scrape: "true"
prometheus.io/port: "8501"
prometheus.io/path: "/metrics"
{{- end }}
