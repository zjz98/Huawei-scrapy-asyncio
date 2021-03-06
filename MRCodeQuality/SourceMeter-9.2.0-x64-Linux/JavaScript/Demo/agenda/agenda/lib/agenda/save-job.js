'use strict';
const debug = require('debug')('agenda:saveJob');
const utils = require('../utils');

const processJobs = utils.processJobs;

/**
 * Save the properties on a job to MongoDB
 * @param {module.Job} job job to save into MongoDB
 * @param {Function} cb called when job is saved or errors
 * @returns {undefined}
 */
module.exports = function(job, cb) {
  debug('attempting to save a job into Agenda instance');

  // Grab information needed to save job but that we don't want to persist in MongoDB
  const fn = cb;
  const self = this;
  const id = job.attrs._id;
  const unique = job.attrs.unique;
  const uniqueOpts = job.attrs.uniqueOpts;

  // Store job as JSON and remove props we don't want to store from object
  const props = job.toJSON();
  delete props._id;
  delete props.unique;
  delete props.uniqueOpts;

  // Store name of agenda queue as last modifier in job data
  props.lastModifiedBy = this._name;
  debug('set job props: \n%O', props);

  // Grab current time and set default query options for MongoDB
  const now = new Date();
  const protect = {};
  let update = {$set: props};
  debug('current time stored as %s', now.toISOString());

  // If the job already had an ID, then update the properties of the job
  // i.e, who last modified it, etc
  if (id) {
    // Update the job and process the resulting data'
    debug('job already has _id, calling findOneAndUpdate() using _id as query');
    this._collection.findOneAndUpdate({
      _id: id
    },
    update, {
      returnOriginal: false
    },
    processDbResult);
  } else if (props.type === 'single') {
    // Job type set to 'single' so...
    // NOTE: Again, not sure about difference between 'single' here and 'once' in job.js
    debug('job with type of "single" found');

    // If the nextRunAt time is older than the current time, "protect" that property, meaning, don't change
    // a scheduled job's next run time!
    if (props.nextRunAt && props.nextRunAt <= now) {
      debug('job has a scheduled nextRunAt time, protecting that field from upsert');
      protect.nextRunAt = props.nextRunAt;
      delete props.nextRunAt;
    }

    // If we have things to protect, set them in MongoDB using $setOnInsert
    if (Object.keys(protect).length > 0) {
      update.$setOnInsert = protect;
    }

    // Try an upsert
    // NOTE: 'single' again, not exactly sure what it means
    debug('calling findOneAndUpdate() with job name and type of "single" as query');
    this._collection.findOneAndUpdate({
      name: props.name,
      type: 'single'
    },
    update, {
      upsert: true,
      returnOriginal: false
    },
    processDbResult);
  } else if (unique) {
    // If we want the job to be unique, then we can upsert based on the 'unique' query object that was passed in
    const query = job.attrs.unique;
    query.name = props.name;
    if (uniqueOpts && uniqueOpts.insertOnly) {
      update = {$setOnInsert: props};
    }

    // Use the 'unique' query object to find an existing job or create a new one
    debug('calling findOneAndUpdate() with unique object as query: \n%O', query);
    this._collection.findOneAndUpdate(query, update, {upsert: true, returnOriginal: false}, processDbResult);
  } else {
    // If all else fails, the job does not exist yet so we just insert it into MongoDB
    debug('using default behavior, inserting new job via insertOne() with props that were set: \n%O', props);
    this._collection.insertOne(props, processDbResult);
  }

  /**
   * Given a result for findOneAndUpdate() or insert() above, determine whether to process
   * the job immediately or to let the processJobs() interval pick it up later
   * @param {Error} err error passed in via MongoDB call as to whether modify call failed or passed
   * @param {*} result the data returned from the findOneAndUpdate() call or insertOne() call
   * @access private
   * @returns {undefined}
   */
  function processDbResult(err, result) {
    // Check if there is an error and either cb(error) or throw if there is no callback
    if (err) {
      debug('processDbResult() received an error, job was not updated/created');
      if (fn) {
        return fn(err);
      }
      throw err;
    } else if (result) {
      debug('processDbResult() called with success, checking whether to process job immediately or not');

      // We have a result from the above calls
      // findAndModify() returns different results than insertOne() so check for that
      let res = result.ops ? result.ops : result.value;
      if (res) {
        // If it is an array, grab the first job
        if (Array.isArray(res)) {
          res = res[0];
        }

        // Grab ID and nextRunAt from MongoDB and store it as an attribute on Job
        job.attrs._id = res._id;
        job.attrs.nextRunAt = res.nextRunAt;

        // If the current job would have been processed in an older scan, process the job immediately
        if (job.attrs.nextRunAt && job.attrs.nextRunAt < self._nextScanAt) {
          debug('[%s:%s] job would have ran by nextScanAt, processing the job immediately', job.attrs.name, res._id);
          processJobs.call(self, job);
        }
      }
    }

    // If we have a callback, return the Job instance
    if (fn) {
      fn(null, job);
    }
  }
};
