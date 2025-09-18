// Update MongoDB schema to include new interaction types
db = db.getSiblingDB('gradvy_preferences');
print('🔧 Updating user_preferences collection schema...');

// Get current validator
var currentValidator = db.runCommand({listCollections: 1, filter: {name: 'user_preferences'}}).cursor.firstBatch[0].options.validator;

// Update interaction types enum
var newInteractionTypes = [
  'course_click', 'quiz_attempt', 'video_watch', 'search', 'page_view',
  'course_enroll', 'course_complete', 'bookmark', 'rating_given',
  'review_written', 'course_abandoned', 'onboarding_started', 'onboarding_flow_completed'
];

print('📝 New interaction types will be:');
newInteractionTypes.forEach(function(type) {
  var isNew = ['onboarding_started', 'onboarding_flow_completed', 'bookmark', 'rating_given', 'review_written', 'course_abandoned'].includes(type);
  var marker = isNew ? ' ✨ NEW' : '';
  print('  - ' + type + marker);
});

// Update the validator
currentValidator['$jsonSchema'].properties.interactions.items.properties.type.enum = newInteractionTypes;

// Apply the updated validation
try {
  db.runCommand({collMod: 'user_preferences', validator: currentValidator});
  print('\n✅ Successfully updated MongoDB schema validation!');
  print('🎉 New interaction types are now allowed');
} catch(e) {
  print('\n❌ Failed to update schema: ' + e);
}