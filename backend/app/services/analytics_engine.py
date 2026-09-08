"""
Advanced Analytics Engine for Blast Furnace Monitoring
Implements Statistical Process Control (SPC), Correlation Analysis, and Root Cause Analysis
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json


@dataclass
class SPCMetrics:
    """Statistical Process Control Metrics"""
    mean: float
    std_dev: float
    ucl: float  # Upper Control Limit
    lcl: float  # Lower Control Limit
    ucl_2sigma: float
    lcl_2sigma: float
    cp: float  # Process Capability
    cpk: float  # Process Capability Index
    violations: List[Dict] = field(default_factory=list)
    trend: str = "stable"  # stable, increasing, decreasing


@dataclass
class CorrelationResult:
    """Correlation Analysis Result"""
    feature_pairs: List[Tuple[str, str]]
    correlation_matrix: pd.DataFrame
    significant_correlations: List[Dict]
    p_values: pd.DataFrame


@dataclass
class RootCauseFinding:
    """Root Cause Analysis Finding"""
    factor: str
    contribution_percentage: float
    correlation_strength: float
    temporal_lag_hours: int
    confidence_score: float
    evidence: List[str]
    recommendation: str


class AdvancedAnalyticsEngine:
    """
    Advanced Analytics Engine implementing:
    1. Statistical Process Control (SPC)
    2. Correlation Analysis
    3. Root Cause Analysis Engine
    """

    def __init__(self):
        self.control_limit_sigma = 3.0
        self.significance_level = 0.05
        self.min_correlation_threshold = 0.6
        self.max_lag_hours = 48

    def calculate_spc(
        self,
        data: pd.Series,
        parameter_name: str,
        target: Optional[float] = None,
        specification_limits: Optional[Tuple[float, float]] = None
    ) -> SPCMetrics:
        """
        Calculate Statistical Process Control metrics for a given parameter.

        Args:
            data: Time series data for the parameter
            parameter_name: Name of the parameter being analyzed
            target: Target value for the parameter (optional)
            specification_limits: Tuple of (lower_spec, upper_spec) limits (optional)

        Returns:
            SPCMetrics object with all control chart metrics
        """
        # Basic statistics
        mean = data.mean()
        std_dev = data.std()

        # Control limits (3-sigma)
        ucl = mean + (self.control_limit_sigma * std_dev)
        lcl = mean - (self.control_limit_sigma * std_dev)

        # 2-sigma warning limits
        ucl_2sigma = mean + (2 * std_dev)
        lcl_2sigma = mean - (2 * std_dev)

        # Process capability (if specification limits provided)
        if specification_limits:
            lower_spec, upper_spec = specification_limits
            cp = (upper_spec - lower_spec) / (6 * std_dev) if std_dev > 0 else float('inf')

            # Cpk calculation
            cpu = (upper_spec - mean) / (3 * std_dev) if std_dev > 0 else float('inf')
            cpl = (mean - lower_spec) / (3 * std_dev) if std_dev > 0 else float('inf')
            cpk = min(cpu, cpl)
        else:
            cp = float('inf')
            cpk = float('inf')

        # Detect violations
        violations = self._detect_control_violations(
            data, mean, std_dev, ucl, lcl, ucl_2sigma, lcl_2sigma
        )

        # Determine trend
        trend = self._detect_trend(data)

        return SPCMetrics(
            mean=mean,
            std_dev=std_dev,
            ucl=ucl,
            lcl=lcl,
            ucl_2sigma=ucl_2sigma,
            lcl_2sigma=lcl_2sigma,
            cp=cp,
            cpk=cpk,
            violations=violations,
            trend=trend
        )

    def _detect_control_violations(
        self,
        data: pd.Series,
        mean: float,
        std_dev: float,
        ucl: float,
        lcl: float,
        ucl_2sigma: float,
        lcl_2sigma: float
    ) -> List[Dict]:
        """Detect control chart violations using Western Electric Rules"""
        violations = []

        # Rule 1: Points beyond 3-sigma
        beyond_3sigma = data[(data > ucl) | (data < lcl)]
        for idx in beyond_3sigma.index:
            violations.append({
                "rule": "Rule 1: Beyond 3-sigma",
                "timestamp": str(idx),
                "value": float(data[idx]),
                "severity": "critical"
            })

        # Rule 2: 2 out of 3 consecutive points beyond 2-sigma
        for i in range(2, len(data)):
            window = data.iloc[i-2:i+1]
            count_beyond_2sigma = sum(
                1 for v in window if v > ucl_2sigma or v < lcl_2sigma
            )
            if count_beyond_2sigma >= 2:
                violations.append({
                    "rule": "Rule 2: 2 of 3 beyond 2-sigma",
                    "timestamp": str(data.index[i]),
                    "value": float(data.iloc[i]),
                    "severity": "warning"
                })

        # Rule 3: 8 consecutive points on one side of mean
        for i in range(7, len(data)):
            window = data.iloc[i-7:i+1]
            if all(v > mean for v in window) or all(v < mean for v in window):
                violations.append({
                    "rule": "Rule 3: 8 consecutive on one side",
                    "timestamp": str(data.index[i]),
                    "value": float(data.iloc[i]),
                    "severity": "warning"
                })

        # Rule 4: 6 consecutive points trending up or down
        for i in range(5, len(data)):
            window = data.iloc[i-5:i+1]
            diffs = window.diff().dropna()
            if all(d > 0 for d in diffs) or all(d < 0 for d in diffs):
                violations.append({
                    "rule": "Rule 4: 6 consecutive trending",
                    "timestamp": str(data.index[i]),
                    "value": float(data.iloc[i]),
                    "severity": "warning"
                })

        return violations

    def _detect_trend(self, data: pd.Series) -> str:
        """Detect overall trend in the data"""
        if len(data) < 3:
            return "insufficient_data"

        # Linear regression to detect trend
        x = np.arange(len(data))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, data.values)

        if p_value > self.significance_level:
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"

    def analyze_correlations(
        self,
        df: pd.DataFrame,
        method: str = 'pearson'
    ) -> CorrelationResult:
        """
        Perform comprehensive correlation analysis on multiple parameters.

        Args:
            df: DataFrame with multiple time series columns
            method: Correlation method ('pearson', 'spearman', 'kendall')

        Returns:
            CorrelationResult with correlation matrices and significant findings
        """
        # Calculate correlation matrix
        corr_matrix = df.corr(method=method)

        # Calculate p-values for correlations
        p_values = self._calculate_correlation_pvalues(df, method)

        # Find significant correlations
        significant_correlations = []
        features = df.columns.tolist()

        for i, feat1 in enumerate(features):
            for j, feat2 in enumerate(features):
                if i >= j:  # Skip diagonal and duplicates
                    continue

                corr_value = corr_matrix.loc[feat1, feat2]
                p_value = p_values.loc[feat1, feat2]

                if abs(corr_value) >= self.min_correlation_threshold and p_value < self.significance_level:
                    significant_correlations.append({
                        "feature_1": feat1,
                        "feature_2": feat2,
                        "correlation": float(corr_value),
                        "p_value": float(p_value),
                        "strength": self._interpret_correlation_strength(abs(corr_value)),
                        "direction": "positive" if corr_value > 0 else "negative"
                    })

        # Sort by absolute correlation strength
        significant_correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        # Generate feature pairs
        feature_pairs = [
            (feat1, feat2) for feat1 in features for feat2 in features if feat1 < feat2
        ]

        return CorrelationResult(
            feature_pairs=feature_pairs,
            correlation_matrix=corr_matrix,
            significant_correlations=significant_correlations,
            p_values=p_values
        )

    def _calculate_correlation_pvalues(
        self,
        df: pd.DataFrame,
        method: str = 'pearson'
    ) -> pd.DataFrame:
        """Calculate p-values for correlation matrix"""
        n = len(df)
        features = df.columns.tolist()
        p_values = pd.DataFrame(
            np.ones((len(features), len(features))),
            index=features,
            columns=features
        )

        for i, feat1 in enumerate(features):
            for j, feat2 in enumerate(features):
                if i >= j:
                    continue

                if method == 'pearson':
                    corr, p_val = stats.pearsonr(df[feat1].dropna(), df[feat2].dropna())
                elif method == 'spearman':
                    corr, p_val = stats.spearmanr(df[feat1].dropna(), df[feat2].dropna())
                elif method == 'kendall':
                    corr, p_val = stats.kendalltau(df[feat1].dropna(), df[feat2].dropna())
                else:
                    p_val = 0.0

                p_values.loc[feat1, feat2] = p_val
                p_values.loc[feat2, feat1] = p_val

        return p_values

    def _interpret_correlation_strength(self, corr: float) -> str:
        """Interpret correlation strength"""
        if corr >= 0.9:
            return "very_strong"
        elif corr >= 0.7:
            return "strong"
        elif corr >= 0.5:
            return "moderate"
        elif corr >= 0.3:
            return "weak"
        else:
            return "very_weak"

    def perform_root_cause_analysis(
        self,
        target_parameter: str,
        candidate_factors: List[str],
        df: pd.DataFrame,
        anomaly_timestamp: Optional[datetime] = None
    ) -> List[RootCauseFinding]:
        """
        Perform root cause analysis to identify factors contributing to anomalies.

        Args:
            target_parameter: The parameter showing anomalous behavior
            candidate_factors: List of potential causal factors to analyze
            df: DataFrame containing all time series data
            anomaly_timestamp: Timestamp of the anomaly (optional, uses latest if None)

        Returns:
            List of RootCauseFinding objects ranked by contribution
        """
        findings = []

        if anomaly_timestamp is None:
            anomaly_timestamp = df.index[-1]

        target_data = df[target_parameter]

        for factor in candidate_factors:
            if factor not in df.columns or factor == target_parameter:
                continue

            factor_data = df[factor]

            # 1. Calculate correlation strength
            corr, p_value = stats.pearsonr(
                target_data.dropna(),
                factor_data.dropna()
            )

            if p_value > self.significance_level:
                continue  # Not statistically significant

            # 2. Analyze temporal lag (does factor change before target?)
            optimal_lag, lag_correlation = self._find_optimal_lag(
                target_data, factor_data, max_lag=self.max_lag_hours
            )

            # 3. Calculate contribution percentage using variance decomposition
            contribution = self._calculate_contribution_percentage(
                target_data, factor_data, corr
            )

            # 4. Generate confidence score based on multiple factors
            confidence_score = self._calculate_confidence_score(
                correlation=abs(corr),
                p_value=p_value,
                lag_correlation=lag_correlation,
                sample_size=len(target_data.dropna())
            )

            # 5. Generate evidence and recommendations
            evidence = self._generate_evidence(
                factor=factor,
                correlation=corr,
                p_value=p_value,
                optimal_lag=optimal_lag,
                contribution=contribution
            )

            recommendation = self._generate_recommendation(
                factor=factor,
                correlation=corr,
                lag=optimal_lag,
                contribution=contribution
            )

            finding = RootCauseFinding(
                factor=factor,
                contribution_percentage=contribution,
                correlation_strength=corr,
                temporal_lag_hours=optimal_lag,
                confidence_score=confidence_score,
                evidence=evidence,
                recommendation=recommendation
            )

            findings.append(finding)

        # Sort by contribution percentage
        findings.sort(key=lambda x: x.contribution_percentage, reverse=True)

        return findings

    def _find_optimal_lag(
        self,
        target: pd.Series,
        factor: pd.Series,
        max_lag: int = 48
    ) -> Tuple[int, float]:
        """Find optimal temporal lag between factor and target"""
        best_lag = 0
        best_corr = 0.0

        for lag in range(0, min(max_lag, len(factor) - 1)):
            if lag == 0:
                shifted_factor = factor
            else:
                shifted_factor = factor.shift(lag)

            # Calculate correlation with lagged factor
            valid_mask = target.notna() & shifted_factor.notna()
            if valid_mask.sum() < 10:  # Need minimum samples
                continue

            corr, _ = stats.pearsonr(
                target[valid_mask],
                shifted_factor[valid_mask]
            )

            if abs(corr) > abs(best_corr):
                best_corr = corr
                best_lag = lag

        return best_lag, best_corr

    def _calculate_contribution_percentage(
        self,
        target: pd.Series,
        factor: pd.Series,
        correlation: float
    ) -> float:
        """Calculate percentage contribution of factor to target variance"""
        # R-squared gives proportion of variance explained
        r_squared = correlation ** 2
        return min(r_squared * 100, 100.0)  # Cap at 100%

    def _calculate_confidence_score(
        self,
        correlation: float,
        p_value: float,
        lag_correlation: float,
        sample_size: int
    ) -> float:
        """Calculate overall confidence score for the finding"""
        # Weight different factors
        corr_weight = 0.4
        significance_weight = 0.3
        lag_weight = 0.2
        sample_weight = 0.1

        # Normalize components
        corr_score = correlation
        significance_score = max(0, 1 - (p_value / self.significance_level))
        lag_score = abs(lag_correlation)
        sample_score = min(sample_size / 1000, 1.0)  # Normalize to 1000 samples

        confidence = (
            corr_weight * corr_score +
            significance_weight * significance_score +
            lag_weight * lag_score +
            sample_weight * sample_score
        )

        return min(confidence, 1.0)

    def _generate_evidence(
        self,
        factor: str,
        correlation: float,
        p_value: float,
        optimal_lag: int,
        contribution: float
    ) -> List[str]:
        """Generate evidence statements for the finding"""
        evidence = []

        evidence.append(
            f"Strong {'positive' if correlation > 0 else 'negative'} correlation "
            f"(r={correlation:.3f}, p={p_value:.4f}) between {factor} and target parameter"
        )

        if optimal_lag > 0:
            evidence.append(
                f"{factor} changes precede target parameter changes by {optimal_lag} hours, "
                f"suggesting causal relationship"
            )

        evidence.append(
            f"{factor} explains approximately {contribution:.1f}% of variance in target parameter"
        )

        return evidence

    def _generate_recommendation(
        self,
        factor: str,
        correlation: float,
        lag: int,
        contribution: float
    ) -> str:
        """Generate actionable recommendation based on finding"""
        direction = "increase" if correlation > 0 else "decrease"
        opposite_direction = "decrease" if correlation > 0 else "increase"

        if contribution > 50:
            priority = "HIGH PRIORITY"
        elif contribution > 30:
            priority = "MEDIUM PRIORITY"
        else:
            priority = "LOW PRIORITY"

        if lag > 0:
            recommendation = (
                f"{priority}: Monitor {factor} closely. Changes in {factor} lead to "
                f"changes in target parameter after {lag} hours. To {opposite_direction} "
                f"the target parameter, consider {direction.lower()}ing {factor} proactively."
            )
        else:
            recommendation = (
                f"{priority}: Strong concurrent relationship detected. To influence "
                f"target parameter, consider {direction.lower()}ing {factor}. "
                f"Immediate effect expected."
            )

        return recommendation

    def generate_analytics_report(
        self,
        df: pd.DataFrame,
        target_parameters: List[str],
        candidate_factors: List[str]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive analytics report combining all analyses.

        Args:
            df: DataFrame with all time series data
            target_parameters: List of parameters to analyze with SPC
            candidate_factors: List of factors for root cause analysis

        Returns:
            Dictionary containing complete analytics report
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "data_summary": {
                "time_range": {
                    "start": str(df.index.min()),
                    "end": str(df.index.max()),
                    "duration_hours": (df.index.max() - df.index.min()).total_seconds() / 3600
                },
                "total_records": len(df),
                "parameters_analyzed": len(df.columns)
            },
            "spc_analysis": {},
            "correlation_analysis": {},
            "root_cause_analysis": {},
            "executive_summary": []
        }

        # SPC Analysis for each target parameter
        for param in target_parameters:
            if param not in df.columns:
                continue

            spc_result = self.calculate_spc(df[param], param)
            report["spc_analysis"][param] = {
                "mean": float(spc_result.mean),
                "std_dev": float(spc_result.std_dev),
                "ucl": float(spc_result.ucl),
                "lcl": float(spc_result.lcl),
                "cp": float(spc_result.cp) if spc_result.cp != float('inf') else None,
                "cpk": float(spc_result.cpk) if spc_result.cpk != float('inf') else None,
                "trend": spc_result.trend,
                "violation_count": len(spc_result.violations),
                "violations": spc_result.violations[:10]  # Top 10 violations
            }

            # Add to executive summary if violations found
            if len(spc_result.violations) > 0:
                critical_violations = [v for v in spc_result.violations if v["severity"] == "critical"]
                report["executive_summary"].append(
                    f"⚠️ {param}: {len(critical_violations)} critical control violations detected. "
                    f"Current trend: {spc_result.trend}"
                )

        # Correlation Analysis
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) > 1:
            corr_result = self.analyze_correlations(numeric_df)
            report["correlation_analysis"] = {
                "significant_correlations": corr_result.significant_correlations[:20],  # Top 20
                "total_significant_pairs": len(corr_result.significant_correlations),
                "correlation_matrix": corr_result.correlation_matrix.to_dict()
            }

            if len(corr_result.significant_correlations) > 0:
                top_corr = corr_result.significant_correlations[0]
                report["executive_summary"].append(
                    f"📊 Strongest correlation: {top_corr['feature_1']} ↔ {top_corr['feature_2']} "
                    f"(r={top_corr['correlation']:.3f})"
                )

        # Root Cause Analysis for each target parameter
        for param in target_parameters:
            if param not in df.columns:
                continue

            rca_findings = self.perform_root_cause_analysis(
                target_parameter=param,
                candidate_factors=candidate_factors,
                df=df
            )

            report["root_cause_analysis"][param] = [
                {
                    "factor": finding.factor,
                    "contribution_percentage": float(finding.contribution_percentage),
                    "correlation_strength": float(finding.correlation_strength),
                    "temporal_lag_hours": finding.temporal_lag_hours,
                    "confidence_score": float(finding.confidence_score),
                    "evidence": finding.evidence,
                    "recommendation": finding.recommendation
                }
                for finding in rca_findings[:5]  # Top 5 findings
            ]

            if len(rca_findings) > 0:
                top_finding = rca_findings[0]
                report["executive_summary"].append(
                    f"🔍 Primary driver for {param}: {top_finding.factor} "
                    f"(contributes {top_finding.contribution_percentage:.1f}% of variance)"
                )

        return report


# Convenience function for quick analysis
def quick_analytics(df: pd.DataFrame, target_params: List[str]) -> Dict[str, Any]:
    """
    Quick analytics function for immediate insights.

    Args:
        df: DataFrame with time series data
        target_params: List of target parameters to analyze

    Returns:
        Quick analytics summary
    """
    engine = AdvancedAnalyticsEngine()
    all_columns = df.columns.tolist()
    candidate_factors = [col for col in all_columns if col not in target_params]

    return engine.generate_analytics_report(
        df=df,
        target_parameters=target_params,
        candidate_factors=candidate_factors
    )
