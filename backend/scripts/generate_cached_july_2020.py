"""
Generate cached July 2020 response for demo backup

Run this script to create a complete, pre-generated response
that can be loaded instantly during demos.
"""

import sys
import os
import json
import asyncio
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scenarios.july_2020_fire import load_july_2020_scenario
from agents.damage_assessment import DamageAssessmentAgent
from agents.population_impact import PopulationImpactAgent
from agents.routing import RoutingAgent
from agents.resource_allocation import ResourceAllocationAgent
from agents.prediction import PredictionAgent


async def generate_cached_response():
    """Generate complete cached response"""
    print("Generating cached July 2020 response...\n")

    # Load scenario
    scenario_config = load_july_2020_scenario()
    print("[OK] Loaded scenario configuration")

    # Create disaster object
    disaster = {
        'disaster_id': 'july-2020-cached-demo',
        'type': 'wildfire',
        'location': scenario_config['disaster']['location'],
        'severity': 'high',
        'status': 'complete',
        'created_at': '2020-07-15T14:30:00Z',
        'metadata': {
            'scenario': 'july_2020_backtest',
            'cached': True,
            'historical': True,
        },
        'data': {
            'fire_perimeter': scenario_config['fire_perimeter'],
            'weather': scenario_config['weather'],
        },
    }
    print("[OK] Created disaster object")

    # Run all agents
    print("\nRunning agents...")

    damage_agent = DamageAssessmentAgent()
    damage_result = await damage_agent.analyze({}, 'wildfire', scenario_config)
    print("[OK] Damage assessment complete")

    pop_agent = PopulationImpactAgent()
    pop_result = await pop_agent.analyze({}, {}, scenario_config)
    print("[OK] Population impact complete")

    routing_agent = RoutingAgent()
    routing_result = await routing_agent.analyze({}, {}, {}, scenario_config)
    print("[OK] Routing complete")

    resource_agent = ResourceAllocationAgent()
    resource_result = await resource_agent.analyze({}, {}, {}, scenario_config)
    print("[OK] Resource allocation complete")

    pred_agent = PredictionAgent()
    pred_result = await pred_agent.analyze(disaster, {}, scenario_config)
    print("[OK] Predictions complete")

    # Create complete plan
    plan = {
        'disaster_id': 'july-2020-cached-demo',
        'generated_at': '2020-07-15T14:31:00Z',
        'confidence': 0.89,
        'executive_summary': """CRITICAL WUI FIRE AT HWY 407/410 INTERCHANGE. 40-acre grass fire spreading at 3.8 km/h threatening 2,000 residents and major highway infrastructure. RECOMMEND IMMEDIATE PROACTIVE CLOSURE OF HWY 407 EASTBOUND LANES within 2.5 hours to prevent evacuation gridlock. Request mutual aid from Mississauga Fire and Caledon Fire immediately - Brampton resources insufficient for WUI fire of this scale.""",

        'situation_overview': """A rapidly spreading 40-acre wildland-urban interface fire has been detected via satellite at the Highway 407/410 interchange in northwest Brampton. Current weather conditions are extreme: 32°C temperature, 18% humidity, and 25 km/h westerly winds driving the fire directly toward Highway 407 eastbound lanes. The fire is spreading at 3.8 km/h through grass and brush fuel with high intensity. Approximately 2,000 residents are in the immediate impact zone, including 280 elderly residents and 420 children requiring priority evacuation assistance. Multiple critical facilities are at risk including Mayfield Secondary School (850 students) and Williams Parkway Seniors Center (95 residents). Highway 407, which carries 400,000 vehicles daily, faces closure within 2.5 hours if fire continues current trajectory, creating potential for catastrophic traffic gridlock during evacuation. Immediate action required to prevent loss of life and infrastructure.""",

        'affected_areas': damage_result,
        'population_impact': pop_result,
        'evacuation_plan': routing_result,
        'resource_deployment': resource_result,
        'timeline_predictions': pred_result,

        'communication_templates': {
            'en': "EMERGENCY: Wildfire at HWY 407/410. Mandatory evacuation for residents within 2km. Proceed immediately to Brampton Soccer Centre via Bovaird Dr. Highway 407 closing soon. Follow official instructions. DO NOT RETURN.",
            'pa': "ਐਮਰਜੈਂਸੀ: ਹਾਈਵੇਅ 407/410 ਤੇ ਜੰਗਲ ਦੀ ਅੱਗ। 2km ਦੇ ਅੰਦਰ ਵਸਨੀਕਾਂ ਲਈ ਲਾਜ਼ਮੀ ਨਿਕਾਸੀ। ਤੁਰੰਤ ਬੋਵੇਅਰਡ ਡਰਾਈਵ ਰਾਹੀਂ ਬ੍ਰੈਂਪਟਨ ਸੌਕਰ ਸੈਂਟਰ ਜਾਓ। ਹਾਈਵੇਅ 407 ਜਲਦੀ ਬੰਦ ਹੋ ਰਿਹਾ ਹੈ। ਵਾਪਸ ਨਾ ਆਉ।",
            'hi': "आपातकाल: HWY 407/410 पर जंगल की आग। 2km के भीतर निवासियों के लिए अनिवार्य निकासी। तुरंत बोवेयर्ड ड्राइव के माध्यम से ब्रैम्पटन सॉकर सेंटर जाएं। हाईवे 407 जल्द बंद हो रहा है। वापस न लौटें।",
        },

        'maps': [
            {
                'title': 'Fire Perimeter and Danger Zone',
                'type': 'danger_zone',
            },
            {
                'title': 'Evacuation Routes',
                'type': 'evacuation_routes',
            },
        ],

        'metadata': {
            'scenario': 'july_2020_backtest',
            'cached': True,
            'generation_time_seconds': 0.5,
        },
    }
    print("[OK] Plan assembled")

    # Complete response object
    response = {
        'disaster': disaster,
        'plan': plan,
        'agent_outputs': {
            'damage_assessment': damage_result,
            'population_impact': pop_result,
            'routing': routing_result,
            'resource_allocation': resource_result,
            'predictions': pred_result,
        },
        'cached_metadata': {
            'generated_at': datetime.now().isoformat(),
            'purpose': 'demo_backup',
            'scenario': 'july_2020_backtest',
            'version': '1.0',
        },
    }

    # Save to file
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cached_data')
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, 'july_2020_response.json')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(response, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCESS] Cached response saved to: {output_path}")
    print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")

    return response


if __name__ == '__main__':
    asyncio.run(generate_cached_response())
