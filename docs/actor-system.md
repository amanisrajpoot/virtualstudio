# Actor System

Subsystem: 3

Status: implemented as a Godot 4 runtime framework, actor state schema, and
architecture/API documentation.

## Purpose

Every character in StoryForge should use the same actor framework.

Actors are not hand-scripted per character. A `halku`, `policeman`,
`teacher`, or `villager_male` scene should expose the same core runtime API:

- `move_to()`
- `speak()`
- `look_at()`
- `perform_intent()`
- `pickup()`
- `drop()`

This keeps later Director, Timeline, Intent, Camera, and Renderer systems able
to control characters deterministically.

## Folder Structure

```text
godot_runtime/
  addons/
    storyforge/
      actors/
        actor_state.gd
        actor_events.gd
        base_actor.gd
schemas/
  actor_system/
    actor_state.schema.json
docs/
  actor-system.md
```

## Architecture

```text
Actor Asset
-> StoryForgeBaseActor
-> StoryForgeActorState
-> NavigationAgent3D
-> SemanticWorldResolver
-> ActorEvents
-> Future Timeline / Intent / Director systems
```

Main runtime classes:

- `StoryForgeBaseActor`: shared `CharacterBody3D` base class for all actors.
- `StoryForgeActorState`: serializable state resource.
- `StoryForgeActorEvents`: optional event bus for decoupled communication.

## Actor Properties

All actors expose:

- `actor_id`
- `emotion`
- `energy`
- `attention`
- `inventory`
- `current_anchor`
- `walk_speed`
- `run_speed`
- `arrival_distance`
- `semantic_world_resolver_path`
- `event_bus_path`
- `navigation_agent_path`

Runtime state snapshot:

```json
{
  "id": "halku",
  "emotion": "neutral",
  "energy": 100,
  "attention": "",
  "inventory": ["moonlight_bottle"],
  "current_anchor": "stall_front",
  "machine_state": "idle"
}
```

Schema:

```text
schemas/actor_system/actor_state.schema.json
```

## State Machine

Supported states:

- `idle`
- `walk`
- `talk`
- `run`
- `interact`

State transitions are internal to the base actor:

- `move_to(..., false)` -> `walk`
- `move_to(..., true)` -> `run`
- movement complete -> `idle`
- `speak()` -> `talk`
- `perform_intent()` -> `interact`
- `complete_intent()` -> `idle`

The actor state machine does not choose story behavior. It only executes
commands from later systems.

## Godot Base Actor

File:

```text
godot_runtime/addons/storyforge/actors/base_actor.gd
```

Attach `StoryForgeBaseActor` to a character scene root that extends
`CharacterBody3D`, or make character roots inherit from it.

The actor will create a `NavigationAgent3D` child automatically if one is not
assigned or found.

## Navigation

Movement is anchor-based.

Example:

```gdscript
actor.semantic_world_resolver_path = resolver.get_path()
actor.move_to("stall_front")
```

Equivalent dictionary form:

```gdscript
actor.move_to({
    "anchor": "stall_front",
    "relation": "at",
    "distance": "near"
})
```

Run movement:

```gdscript
actor.move_to("entrance", true)
```

The actor asks `StoryForgeSemanticWorldResolver` for a runtime position and then
uses `NavigationAgent3D`. Coordinates remain internal to Godot.

## Speech

```gdscript
actor.speak("What exactly are you selling?", {"voice": "voice_stern_male_v1"}, 2.0)
```

This sets state to `talk`, emits events, and optionally returns to `idle` after
the duration. Actual voice synthesis is not implemented here; it belongs to the
later Voice System.

## Attention And Look Target

```gdscript
actor.look_at(Vector3(0, 0, 0))
actor.look_at_target("market_center")
actor.look_at_target(other_actor)
actor.look_at_anchor({"anchor": "stall_front"})
```

`look_at()` keeps Godot's native `Node3D.look_at()` signature and accepts a
`Vector3`.

Semantic target helpers support anchor IDs, anchor reference dictionaries, and
`Node3D` targets:

- `look_at_target()`
- `look_at_anchor()`

## Inventory

```gdscript
actor.pickup("moonlight_bottle")
actor.drop("moonlight_bottle")
```

Inventory is stored in actor state as an array of stable item IDs. These IDs
should correspond to prop assets or world-state items later.

## Intent Execution Boundary

```gdscript
actor.perform_intent("question", {"target": "halku"})
```

This subsystem does not implement the Intent System.

`perform_intent()` only:

- sets actor state to `interact`
- emits an `intent_requested` signal
- publishes the same event to `StoryForgeActorEvents`
- returns normalized event context

Subsystem 4 will own intent definitions and intent-to-action mapping.

When a future intent handler finishes:

```gdscript
actor.complete_intent("question", {"status": "done"})
```

## Event Driven Communication

File:

```text
godot_runtime/addons/storyforge/actors/actor_events.gd
```

Signals:

- `actor_registered(actor_id, actor)`
- `actor_state_changed(actor_id, state)`
- `actor_move_requested(actor_id, anchor_reference)`
- `actor_move_completed(actor_id, anchor_reference)`
- `actor_spoke(actor_id, text, metadata)`
- `actor_looked_at(actor_id, target)`
- `actor_inventory_changed(actor_id, inventory)`
- `actor_intent_requested(actor_id, intent_id, context)`
- `actor_intent_completed(actor_id, intent_id, result)`
- `actor_error(actor_id, message)`

Actors also emit matching local signals, so a scene can either listen directly
to one actor or use a shared event bus.

## Emotion And Energy

Public functions:

```gdscript
actor.set_emotion("suspicious")
actor.set_energy(72.0)
actor.set_attention("halku")
```

Emotion is a string contract for now. Later subsystems can define an enum or
emotion model if needed, but the actor runtime should not depend on AI or
dialogue systems.

## State Snapshots

Serialize current state:

```gdscript
var snapshot := actor.state_snapshot()
```

Restore state:

```gdscript
actor.apply_state_snapshot(snapshot)
```

This is intentionally compatible with the future World State Manager.

## Example Scene Setup

```gdscript
var event_bus := StoryForgeActorEvents.new()
add_child(event_bus)

var resolver := StoryForgeSemanticWorldResolver.new()
add_child(resolver)
resolver.index_scene(get_tree().current_scene)

var halku := $Halku as StoryForgeBaseActor
halku.event_bus_path = event_bus.get_path()
halku.semantic_world_resolver_path = resolver.get_path()

halku.move_to("stall_front")
halku.pickup("moonlight_bottle")
halku.speak("Fresh bottled moonlight!", {}, 2.0)
```

## Boundaries

Implemented here:

- Base actor class.
- Actor state.
- Actor state machine.
- Navigation through semantic anchors.
- Emotion and energy state.
- Inventory operations.
- Intent request event hook.
- Event-driven communication.

Not implemented here:

- Intent definitions or mappings.
- Timeline sequencing.
- Camera direction.
- Rendering.
- Story compilation.
- Voice synthesis.
- Plugin UI.
- Web app.
