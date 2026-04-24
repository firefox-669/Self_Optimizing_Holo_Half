"""
验证 A/B 测试框架是否正确实现
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_ab_testing():
    """测试 A/B 测试功能"""
    print("🧪 Testing A/B Testing Framework...\n")
    
    try:
        from user_scoring.ab_testing import ABTestFramework, TestType, ab_test, Decision
        print("✅ Import successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # 测试 1: Z-test
    print("\n1. Testing Z-test...")
    try:
        variant_a = [3.5, 3.8, 3.6, 3.9, 3.7] * 20  # 100 samples
        variant_b = [4.0, 4.2, 4.1, 4.3, 4.0] * 20
        
        framework = ABTestFramework()
        result = framework.run_z_test(variant_a, variant_b)
        
        assert result.variant_a_mean > 0, "Mean A should be positive"
        assert result.variant_b_mean > 0, "Mean B should be positive"
        assert 0 <= result.p_value <= 1, "P-value should be between 0 and 1"
        assert isinstance(result.decision, Decision), "Should return Decision enum"
        
        print(f"   ✅ Z-test passed (p={result.p_value:.6f}, decision={result.decision.value})")
    except Exception as e:
        print(f"   ❌ Z-test failed: {e}")
        return False
    
    # 测试 2: T-test
    print("\n2. Testing T-test...")
    try:
        variant_a = [3.5, 3.8, 3.6, 3.9, 3.7]
        variant_b = [4.0, 4.2, 4.1, 4.3, 4.0]
        
        result = ab_test(variant_a, variant_b, test_type=TestType.T_TEST)
        
        assert result.test_statistic != 0 or result.p_value == 1.0, "Should calculate t-statistic"
        print(f"   ✅ T-test passed (p={result.p_value:.6f})")
    except Exception as e:
        print(f"   ❌ T-test failed: {e}")
        return False
    
    # 测试 3: Paired T-test
    print("\n3. Testing Paired T-test...")
    try:
        before = [3.5, 3.8, 3.6, 3.9, 3.7]
        after = [4.0, 4.2, 4.1, 4.3, 4.0]
        
        result = framework.run_t_test(before, after, paired=True)
        print(f"   ✅ Paired T-test passed (p={result.p_value:.6f})")
    except Exception as e:
        print(f"   ❌ Paired T-test failed: {e}")
        return False
    
    # 测试 4: Sample size calculation
    print("\n4. Testing sample size calculation...")
    try:
        n = framework.calculate_sample_size(
            min_detectable_effect=0.1,
            power=0.8,
            variance=1.0
        )
        assert n > 0, "Sample size should be positive"
        print(f"   ✅ Sample size calculation passed (n={n} per group)")
    except Exception as e:
        print(f"   ❌ Sample size calculation failed: {e}")
        return False
    
    # 测试 5: Decision making
    print("\n5. Testing decision logic...")
    try:
        # Significant improvement
        result_improve = framework._make_decision(3.5, 4.0, True, 0.5)
        assert result_improve == Decision.KEEP_AND_PROMOTE, "Should promote on significant improvement"
        
        # Significant decline
        result_decline = framework._make_decision(4.0, 3.5, True, -0.5)
        assert result_decline == Decision.ROLLBACK, "Should rollback on significant decline"
        
        # No significant difference
        result_keep = framework._make_decision(3.5, 3.6, False, 0.1)
        assert result_keep == Decision.KEEP, "Should keep on no significant difference"
        
        print(f"   ✅ Decision logic passed")
    except Exception as e:
        print(f"   ❌ Decision logic failed: {e}")
        return False
    
    # 测试 6: Result interpretation
    print("\n6. Testing result interpretation...")
    try:
        variant_a = [3.5, 3.8, 3.6]
        variant_b = [4.0, 4.2, 4.1]
        result = framework.run_t_test(variant_a, variant_b)
        interpretation = framework.interpret_result(result)
        
        assert "A/B Test Results" in interpretation, "Should contain header"
        assert "Variant A Mean" in interpretation, "Should show Variant A mean"
        assert "Decision:" in interpretation, "Should show decision"
        
        print(f"   ✅ Result interpretation passed")
    except Exception as e:
        print(f"   ❌ Result interpretation failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ All tests passed! A/B Testing Framework is working!")
    print("="*60)
    return True


if __name__ == "__main__":
    success = test_ab_testing()
    sys.exit(0 if success else 1)
