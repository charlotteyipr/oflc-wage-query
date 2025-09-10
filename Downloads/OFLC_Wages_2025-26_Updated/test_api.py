#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本
测试OFLC薪资查询系统的三种查询功能
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_forward_search():
    """测试根据职位名称查询"""
    print("=== 测试根据职位名称查询 ===")
    url = f"{BASE_URL}/api/search/forward"
    data = {
        "position": "Manager",
        "location": "California",
        "county": "Orange County"
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 根据职位名称查询成功，找到 {len(result['results'])} 条结果")
            if result['results']:
                first_result = result['results'][0]
                print(f"   示例结果: {first_result['occupation']} in {first_result['location']}")
                print(f"   Level 1-4 年薪: ${first_result['level1']}, ${first_result['level2']}, ${first_result['level3']}, ${first_result['level4']}")
        else:
            print(f"❌ 根据职位名称查询失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 根据职位名称查询异常: {e}")

def test_reverse_search():
    """测试根据薪资查询"""
    print("\n=== 测试根据薪资查询 ===")
    url = f"{BASE_URL}/api/search/reverse"
    data = {
        "min_salary": 60000.0,  # 年薪
        "max_salary": 100000.0,  # 年薪
        "location": "California",
        "county": "Orange County"
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 根据薪资查询成功，找到 {len(result['results'])} 条结果")
            if result['results']:
                first_result = result['results'][0]
                print(f"   示例结果: {first_result['occupation']} in {first_result['location']}")
                print(f"   符合薪资范围的Level: {[f'Level {level['level']}: ${level['salary']}' for level in first_result['matching_levels']]}")
        else:
            print(f"❌ 根据薪资查询失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 根据薪资查询异常: {e}")

def test_location_search():
    """测试地区查询"""
    print("\n=== 测试地区查询 ===")
    url = f"{BASE_URL}/api/search/location"
    data = {
        "position": "Marketing Manager",
        "target_level": 2,
        "target_salary": 80000.0  # 年薪
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 地区查询成功，找到 {len(result['results'])} 个符合条件的地区")
            if result['results']:
                first_result = result['results'][0]
                print(f"   示例结果: {first_result['occupation']} in {first_result['location']}")
                print(f"   Level {first_result['target_level']} 年薪: ${first_result['target_level_salary']}")
        else:
            print(f"❌ 地区查询失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 地区查询异常: {e}")

def test_homepage():
    """测试主页"""
    print("\n=== 测试主页 ===")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ 主页访问成功")
        else:
            print(f"❌ 主页访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 主页访问异常: {e}")

def test_autocomplete():
    """测试自动完成功能"""
    print("\n=== 测试自动完成功能 ===")
    
    # 测试职位搜索
    try:
        response = requests.get(f"{BASE_URL}/api/search/occupations?q=Manager")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 职位搜索成功，找到 {len(result['occupations'])} 个职位")
            if result['occupations']:
                print(f"   示例: {result['occupations'][0]['title']}")
        else:
            print(f"❌ 职位搜索失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 职位搜索异常: {e}")
    
    # 测试州搜索
    try:
        response = requests.get(f"{BASE_URL}/api/search/states?q=Cal")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 州搜索成功，找到 {len(result['states'])} 个州")
            if result['states']:
                print(f"   示例: {result['states'][0]['state']}")
        else:
            print(f"❌ 州搜索失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 州搜索异常: {e}")
    
    # 测试县搜索
    try:
        response = requests.get(f"{BASE_URL}/api/search/counties?q=Orange")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 县搜索成功，找到 {len(result['counties'])} 个县")
            if result['counties']:
                print(f"   示例: {result['counties'][0]['county']}")
        else:
            print(f"❌ 县搜索失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 县搜索异常: {e}")

if __name__ == "__main__":
    print("开始测试OFLC薪资查询系统...")
    print(f"测试地址: {BASE_URL}")
    
    test_homepage()
    test_autocomplete()
    test_forward_search()
    test_reverse_search()
    test_location_search()
    
    print("\n测试完成！")
